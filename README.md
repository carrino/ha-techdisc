# TechDisc Home Assistant Integration

A Home Assistant custom component that integrates with TechDisc devices to track disc golf throw metrics.

## Features

This integration provides real-time disc golf throw data from your TechDisc device, including:

- **Speed** (mph) - Disc release speed
- **Distance** (ft) - Estimated throw distance
- **Hyzer Angle** (°) - Amount of hyzer, anhyzer is negative
- **Nose Angle** (°) - Angle relative to the launch angle
- **Launch Angle** (°) - Initial flight angle
- **Spin** (rpm) - Disc spin rate
- **Wobble** (°) - Off-axis wobble
- **Throw Type** - Primary and secondary throw classification

## Requirements

- Home Assistant 2023.1.0 or newer
- TechDisc device with active Play or Pro subscription
- TechDisc JWT token (obtained in account settings on https://techdisc.com/settings)
## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository:
   - In HACS, go to "Integrations"
   - Click the three dots menu → "Custom repositories"
   - Add `https://github.com/carrino/ha-techdisc` as an "Integration"
2. Install "TechDisc" from HACS
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/carrino/ha-techdisc/releases)
2. Extract the contents to your `custom_components` directory:
   ```
   custom_components/
   └── techdisc/
       ├── __init__.py
       ├── manifest.json
       ├── config_flow.py
       ├── const.py
       ├── sensor.py
       └── www/
           └── techdisc-card.js
   ```
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## Configuration

### Adding the Integration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "TechDisc"
4. Enter your JWT token when prompted
5. The integration will validate the token and create sensors

## Usage

### Sensors Created

The integration creates the following sensors:

- `sensor.techdisc_speed` - Release speed in mph
- `sensor.techdisc_distance` - Estimated distance in feet
- `sensor.techdisc_hyzer_angle` - Hyzer angle in degrees
- `sensor.techdisc_nose_angle` - Nose angle in degrees
- `sensor.techdisc_launch_angle` - Launch angle in degrees
- `sensor.techdisc_spin` - Spin in RPM
- `sensor.techdisc_wobble` - Wobble in degrees
- `sensor.techdisc_throw_type` - Throw classification

### Custom Dashboard Card

The integration includes a custom Lovelace card for displaying throw metrics in a clean, organized layout.

#### Installing the Card

1. Go to Settings → Dashboards → Resources
2. Add a new resource:
   - URL: `/hacsfiles/techdisc/techdisc-card.js`
   - Resource type: JavaScript Module
3. Save and refresh your browser

#### Using the Card

Add the card to your dashboard with this configuration:

```yaml
type: custom:techdisc-card
title: "Latest Throw"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with TechDisc. TechDisc is a trademark of TechDisc Inc.

