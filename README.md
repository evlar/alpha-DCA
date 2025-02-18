# 🤖 Alpha DCA - Bittensor Automated Staking Tool

Automate your TAO staking across multiple Bittensor subnets with a user-friendly web interface.

## 🚀 Quick Start (Web UI)

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

## 💻 CLI Setup (No GUI)

If you prefer command-line setup:

1. Copy the example config:
```bash
cp example.config.yaml config.yaml
```

2. Edit the config file with your preferred editor:
```bash
nano config.yaml  # or vim config.yaml
```

3. Run the DCA script:
```bash
python3 alpha_DCA.py
```

## 🔄 Running in Background

Whether you're using the web UI or CLI setup, you'll want to run the DCA script (`alpha_DCA.py`) in a persistent session. We recommend using tmux:

```bash
# Start a new tmux session named "alpha-dca"
tmux new -s alpha-dca

# Inside tmux, activate your virtual environment and run the script
source venv/bin/activate
python3 alpha_DCA.py

# Detach from tmux session (but leave it running) by pressing:
# Ctrl+B, then D

# Later, to reattach to the session:
tmux attach -t alpha-dca

# To list all running sessions:
tmux ls

# To kill the session:
tmux kill-session -t alpha-dca
```

After making changes to `config.yaml`, you'll need to stop the current process (Ctrl+C) and restart the script.

## 📈 Allocation Strategy

You can create multiple allocation categories (e.g., "Established", "New-comers", "Shit-coiners") and assign different percentages of your total DCA amount to each. Within each category, distribute the stake across multiple subnets:

```yaml
allocation:
  established:  # 60% of total DCA
    description: Proven subnets with consistent returns
    total_percentage: 90
    subnets:
      '11': 60  # 60% of the 90%
      '64': 40  # 40% of the 90%
  shit_coiners:  # 40% of total DCA
    description: YOLO plays
    total_percentage: 10
    subnets:
      '333': 100  # 100% of the 10%
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