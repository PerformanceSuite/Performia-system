 supercollider`
- Windows: Download from https://supercollider.github.io/

### High latency (>15ms)
1. Reduce buffer size in audio settings
2. Close other audio applications
3. Disable WiFi/Bluetooth during performance
4. Check CPU throttling settings

### "Permission denied" errors
- Linux: Add user to audio group: `sudo usermod -a -G audio $USER`
- Then logout and login again

### Import errors
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Next Steps

1. Adjust personalities in `config/personalities.json`
2. Modify ensemble size in `config/config.yaml`
3. Run performance: `python src/main.py`

For detailed documentation, see the [docs](docs/) directory.
