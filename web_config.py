from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf import CSRFProtect
import yaml
import os
from typing import Dict, Any, List
from alpha_DCA import ConfigValidator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)

def load_config() -> Dict[str, Any]:
    """Load existing config or create default one if it doesn't exist."""
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    return {
        "network": "finney",
        "wallet": {"name": ""},
        "staking": {
            "delegate_hotkey": "",
            "amount_per_cycle": 0.01,
            "interval": 10800
        },
        "allocation": {}
    }

def save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

@app.route('/')
def index():
    """Display the main configuration page."""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current configuration."""
    return jsonify(load_config())

@app.route('/api/config/basic', methods=['POST'])
@csrf.exempt
def update_basic_settings():
    """Update basic network and wallet settings."""
    try:
        config = load_config()
        data = request.get_json()
        
        if not data or 'network' not in data or 'wallet_name' not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        config['network'] = data['network']
        config['wallet']['name'] = data['wallet_name']
        
        try:
            ConfigValidator.validate_network(config['network'])
            ConfigValidator.validate_wallet(config['wallet'])
            save_config(config)
            return jsonify({"status": "success"})
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/config/staking', methods=['POST'])
@csrf.exempt
def update_staking_settings():
    """Update staking settings."""
    try:
        config = load_config()
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        config['staking'].update(data)
        
        try:
            ConfigValidator.validate_staking(config['staking'])
            save_config(config)
            return jsonify({"status": "success"})
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/config/allocation', methods=['POST'])
@csrf.exempt
def update_allocation():
    """Update subnet allocation settings."""
    try:
        config = load_config()
        data = request.get_json()
        
        if not data or 'allocation' not in data:
            return jsonify({"status": "error", "message": "No allocation data provided"}), 400
        
        config['allocation'] = data['allocation']
        
        try:
            ConfigValidator.validate_allocation(config['allocation'])
            save_config(config)
            return jsonify({"status": "success"})
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/validate', methods=['GET'])
def validate_config():
    """Validate the entire configuration."""
    config = load_config()
    errors = []
    
    try:
        ConfigValidator.validate_network(config['network'])
        ConfigValidator.validate_wallet(config['wallet'])
        ConfigValidator.validate_staking(config['staking'])
        ConfigValidator.validate_allocation(config['allocation'])
        return jsonify({
            "status": "valid",
            "errors": []
        })
    except ValueError as e:
        return jsonify({
            "status": "invalid",
            "errors": [str(e)]
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 