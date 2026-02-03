# Skylight Calendar Integration for Home Assistant

A Home Assistant integration that connects your Skylight calendar to Home Assistant.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/mikesir87/skylight-ha`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Skylight Calendar" in the integration list and install

### Manual Installation

1. Copy the `custom_components/skylight_calendar` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Skylight Calendar"
4. Enter your Skylight API credentials

## Features

- View Skylight calendar events in Home Assistant
- Calendar entity for automations and dashboards

## TODO

- [ ] Implement Skylight API client
- [ ] Add event creation/modification
- [ ] Add multiple calendar support
- [ ] Add configuration options
