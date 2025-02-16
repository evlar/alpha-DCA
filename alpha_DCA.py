
import asyncio
import bittensor as bt
import os
import yaml
import getpass
from typing import Dict, Any
from dataclasses import dataclass
import sys

@dataclass
class StakingConfig:
    delegate_hotkey: str
    amount_per_cycle: float
    interval: int

class ConfigValidator:
    @staticmethod
    def validate_network(network: str) -> bool:
        valid_networks = ['finney', 'local']
        if network not in valid_networks:
            raise ValueError(f"Invalid network. Must be one of: {', '.join(valid_networks)}")
        return True

    @staticmethod
    def validate_wallet(wallet: Dict[str, Any]) -> bool:
        required_fields = ['name']
        for field in required_fields:
            if field not in wallet:
                raise ValueError(f"Missing required wallet field: {field}")
        return True

    @staticmethod
    def validate_staking(staking: Dict[str, Any]) -> bool:
        required_fields = {
            'delegate_hotkey': str,
            'amount_per_cycle': (float, int),
            'interval': int
        }
        
        for field, field_type in required_fields.items():
            if field not in staking:
                raise ValueError(f"Missing required staking field: {field}")
            if not isinstance(staking[field], field_type):
                raise ValueError(f"Invalid type for {field}. Expected {field_type}")

        if staking['amount_per_cycle'] < 0.001:
            raise ValueError("amount_per_cycle must be at least 0.001 TAO")
        if staking['interval'] < 300:
            raise ValueError("interval must be at least 300 seconds (5 minutes)")
        
        return True

    @staticmethod
    def validate_allocation(allocation: Dict[str, Any]) -> bool:
        total_percentage = 0
        
        for category, data in allocation.items():
            if not isinstance(data, dict):
                raise ValueError(f"Invalid allocation category format for {category}")
            
            required_fields = ['description', 'total_percentage', 'subnets']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field '{field}' in {category}")
            
            if not isinstance(data['subnets'], dict):
                raise ValueError(f"Subnets must be a dictionary in {category}")
                
            # Validate that subnet percentages sum to 100%
            subnet_total = sum(data['subnets'].values())
            if abs(subnet_total - 100) > 0.01:  # Allow for small floating point differences
                raise ValueError(
                    f"Subnet percentages in {category} must sum to 100%, "
                    f"but they sum to {subnet_total}%"
                )
            
            total_percentage += data['total_percentage']
        
        if total_percentage != 100:
            raise ValueError(f"Total allocation percentage must be 100%, got {total_percentage}%")
        
        return True

async def stake_to_subnet(wallet: bt.wallet, sub: bt.AsyncSubtensor, netuid: int, amount: float, delegate_hotkey: str):
    """Stake TAO to a specified subnet."""
    try:
        success = await sub.add_stake(
            wallet=wallet,
            hotkey_ss58=delegate_hotkey,
            netuid=netuid,
            amount=bt.Balance.from_tao(amount),
            wait_for_inclusion=False,
            wait_for_finalization=False
        )
        print(f"✓ Initiated staking of {amount:.6f} TAO to subnet {netuid}")
        return success
    except Exception as e:
        print(f"✗ Error staking to subnet {netuid}: {str(e)}")
        return False

def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """Load and validate the configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate each section
        ConfigValidator.validate_network(config['network'])
        ConfigValidator.validate_wallet(config['wallet'])
        ConfigValidator.validate_staking(config['staking'])
        ConfigValidator.validate_allocation(config['allocation'])
        
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing configuration file: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration validation error: {str(e)}")
        sys.exit(1)

def get_stake_plan(allocation: Dict[str, Any]) -> Dict[int, float]:
    """Convert allocation configuration into a flat stake plan."""
    stake_plan = {}
    for category_data in allocation.values():
        for netuid, percentage in category_data['subnets'].items():
            stake_plan[int(netuid)] = float(percentage)
    return stake_plan

async def dca_stake():
    """
    Periodically stakes a fixed amount of TAO into specified subnets based on allocation strategy.
    """
    print("🔄 Loading configuration...")
    config = load_and_validate_config('config.yaml')
    
    staking_config = StakingConfig(
        delegate_hotkey=config['staking']['delegate_hotkey'],
        amount_per_cycle=config['staking']['amount_per_cycle'],
        interval=config['staking']['interval']
    )
    
    stake_plan = get_stake_plan(config['allocation'])
    
    print("\n📊 Staking Strategy Summary:")
    print(f"Network: {config['network']}")
    print(f"Wallet: {config['wallet']['name']}")
    print(f"Amount per cycle: {staking_config.amount_per_cycle} TAO")
    print(f"Interval: {staking_config.interval} seconds")
    print("\nAllocation:")
    for category, data in config['allocation'].items():
        print(f"\n{category.replace('_', ' ').title()} ({data['total_percentage']}%):")
        print(f"Description: {data['description']}")
        for netuid, percentage in data['subnets'].items():
            amount = staking_config.amount_per_cycle * (percentage / 100)
            print(f"  - Subnet {netuid}: {percentage}% ({amount:.6f} TAO)")

    async with bt.AsyncSubtensor(config['network']) as sub:
        try:
            wallet = bt.wallet(
                name=config['wallet']['name']
            )

            print("\n🔐 Unlocking wallet...")
            wallet.unlock_coldkey()
            print("✓ Wallet unlocked successfully")
            
            balance = await sub.get_balance(wallet.coldkeypub.ss58_address)
            print(f"💰 Current wallet balance: {balance.tao} TAO")
        except Exception as e:
            print(f"❌ Failed to access wallet: {str(e)}")
            return

        cycle_count = 0
        
        while True:
            cycle_count += 1
            print(f"\n📈 Starting cycle {cycle_count}...")

            balance = await sub.get_balance(wallet.coldkeypub.ss58_address)
            print(f"💰 Current wallet balance: {balance.tao} TAO")
            
            if balance.tao < staking_config.amount_per_cycle:
                print(f"⚠️  Insufficient balance. Need {staking_config.amount_per_cycle} TAO but only have {balance.tao} TAO")
                await asyncio.sleep(staking_config.interval)
                continue

            staking_tasks = []
            for netuid, percentage in stake_plan.items():
                amount = staking_config.amount_per_cycle * (percentage / 100)
                staking_tasks.append(
                    stake_to_subnet(
                        wallet=wallet,
                        sub=sub,
                        netuid=netuid,
                        amount=amount,
                        delegate_hotkey=staking_config.delegate_hotkey
                    )
                )
            
            if staking_tasks:
                print(f"🔄 Initiating {len(staking_tasks)} staking operations...")
                results = await asyncio.gather(*staking_tasks)
                successful = sum(1 for r in results if r)
                print(f"✓ Completed {successful} out of {len(staking_tasks)} staking operations")
            
            print(f"\n✨ Cycle {cycle_count} completed. Waiting for next cycle...")
            await asyncio.sleep(staking_config.interval)

if __name__ == "__main__":
    try:
        asyncio.run(dca_stake())
    except KeyboardInterrupt:
        print("\n👋 Gracefully shutting down...")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")