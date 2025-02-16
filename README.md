# 🤖 Alpha DCA - Bittensor Automated Staking Tool

Automate your TAO staking across multiple Bittensor subnets with a user-friendly web interface.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/alpha-DCA.git
cd alpha-DCA
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Start web interface
python3 web_config.py

# Visit http://localhost:5000 in your browser to configure your staking strategy
```

## 🔄 Running in Background

To run the DCA script in the background with the correct virtual environment:

```bash
# Install PM2 if you haven't already
npm install -g pm2

# Get the absolute path to your virtual environment's Python
VENV_PYTHON=$(which python3)

# Start DCA script with PM2 using the virtual environment's Python
pm2 start alpha_DCA.py --name "alpha-dca" --interpreter $VENV_PYTHON

# Verify it's running with the correct interpreter
pm2 show alpha-dca

# Monitor logs
pm2 logs alpha-dca

# Other useful commands
pm2 stop alpha-dca
pm2 restart alpha-dca
pm2 status
```

Make sure to run these commands while your virtual environment is activated.

## 📈 Allocation Strategy

You can create multiple allocation categories (e.g., "Established", "New-comers", "Shit-coiners") and assign different percentages of your total DCA amount to each. Within each category, distribute the stake across multiple subnets:

```yaml
allocation:
  established:  # 60% of total DCA
    description: Proven subnets
    total_percentage: 60
    subnets:
      1: 70  # 70% of the 60%
      2: 30  # 30% of the 60%
  shit_coiners:  # 40% of total DCA
    description: High risk, high reward subnets
    total_percentage: 40
    subnets:
      11: 50  # 50% of the 40%
      64: 50  # 50% of the 40%
```

## 📝 Configuration Example
```yaml
network: finney
wallet:
  name: your_wallet_name
staking:
  delegate_hotkey: 5HK5tp6t2S59DywmHRWPBVJeJ86T61KjurYqeooqj8sREpeN # Bittensor Guru
  amount_per_cycle: .01  # TAO
  interval: 10800  # seconds
allocation:
  established:
    description: Safe plays
    total_percentage: 90
    subnets:
      '11': 60
      '64': 40
  shit_coiners:
    description: YOLO plays
    total_percentage: 10
    subnets:
      '333': 50
      '111': 50
```

## ✨ Features

- 🌐 Web UI for easy configuration
- 📊 Visual allocation management
- ⚡ Automated periodic staking
- 🔒 Secure wallet handling

## ⚠️ Important

- Ensure sufficient TAO balance
- Keep wallet credentials secure
- Test with small amounts first

---
Made with ❤️ for the Bittensor community