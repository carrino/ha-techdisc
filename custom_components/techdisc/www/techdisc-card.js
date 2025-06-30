class TechDiscCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    // if (!config.entity) { // Removed this check
    //   throw new Error('You need to define an entity');
    // }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateContent();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        .card {
          background: var(--ha-card-background, var(--card-background-color, white));
          border-radius: var(--ha-card-border-radius, 12px);
          box-shadow: var(--ha-card-box-shadow, var(--shadow-elevation-2dp_-_box-shadow));
          padding: 16px;
          margin: 4px;
        }
        .header {
          display: flex;
          align-items: center;
          margin-bottom: 16px;
        }
        .header ha-icon {
          margin-right: 8px;
          color: var(--primary-color);
        }
        .header h2 {
          margin: 0;
          color: var(--primary-text-color);
          font-size: 1.2em;
          font-weight: 500;
        }
        .content-wrapper {
          display: flex;
          gap: 16px;
        }
        .left-column {
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-width: 180px; /* Adjusted min-width */
        }
        .left-column p { /* Style for "Latest Throw" */
          margin: 0;
          font-weight: 500; /* Similar to header h2 */
          color: var(--primary-text-color);
        }
        .left-column span { /* Style for throw type, bearing, time */
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .right-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          flex-grow: 1;
        }
        .metric {
          /* background: var(--secondary-background-color); */ /* Removed */
          border-radius: var(--ha-card-border-radius, 12px); /* Use HA card radius */
          padding: 12px;
          text-align: center;
          background: var(--ha-card-background, var(--card-background-color, white)); /* Use HA card background */
          box-shadow: var(--ha-card-box-shadow, var(--shadow-elevation-2dp_-_box-shadow)); /* Use HA card shadow */
        }
        .metric-label { /* This is the title like "Speed" */
          font-size: 1em; /* Adjusted - similar to MuiTypography-body1 */
          font-weight: 500; /* Adjusted */
          color: var(--primary-text-color); /* Adjusted */
          margin-bottom: 8px; /* Adjusted - similar to MuiTypography-gutterBottom */
          text-transform: none; /* Removed uppercase */
          letter-spacing: normal; /* Reset letter-spacing */
        }
        .metric-value-container { /* New container for value and unit */
          display: flex;
          justify-content: center;
          align-items: baseline; /* Aligns value and unit nicely */
        }
        .metric-value { /* Just the number */
          font-size: 1.6em; /* Increased size */
          font-weight: bold;
          color: var(--primary-text-color); /* Changed from primary-color */
          /* margin-bottom: 4px; */ /* Removed, handled by flex container */
        }
        .metric-unit {
          font-size: 1em; /* Adjusted to be similar to Mui's secondary span */
          color: var(--secondary-text-color);
          margin-left: 4px; /* Space between value and unit */
        }
        .throw-info { /* This class is no longer used, but kept for reference if needed elsewhere */
          margin-top: 16px;
          padding: 12px;
          background: var(--secondary-background-color);
          border-radius: 8px;
        }
        .throw-type {
          font-size: 1.1em;
          font-weight: 500;
          color: var(--primary-text-color);
          margin-bottom: 8px;
        }
        .throw-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 8px;
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .unavailable {
          text-align: center;
          color: var(--secondary-text-color);
          font-style: italic;
          padding: 20px;
        }
      </style>
      <div class="card">
        <div class="header">
          <ha-icon icon="mdi:disc"></ha-icon>
          <h2>${this.config.title || 'TechDisc Metrics'}</h2>
        </div>
        <div id="content"></div>
      </div>
    `;
  }

  updateContent() {
    if (!this._hass) return;

    const content = this.shadowRoot.getElementById('content');
    
    // Get all TechDisc sensors
    const speedEntity = this._hass.states['sensor.techdisc_speed'];
    // const distanceEntity = this._hass.states['sensor.techdisc_distance']; // Not used in the new layout
    const hyzerEntity = this._hass.states['sensor.techdisc_hyzer_angle'];
    const noseEntity = this._hass.states['sensor.techdisc_nose_angle'];
    const rotationEntity = this._hass.states['sensor.techdisc_spin'];
    const launchAngleEntity = this._hass.states['sensor.techdisc_launch_angle'];
    const wobbleEntity = this._hass.states['sensor.techdisc_wobble'];
    const throwTypeEntity = this._hass.states['sensor.techdisc_throw_type'];
    const distanceEntity = this._hass.states['sensor.techdisc_distance']; // Added back for left column
    // const lastThrowTimeEntity = this._hass.states['sensor.techdisc_last_throw_time']; // No longer needed
    // const bearingEntity = this._hass.states['sensor.techdisc_bearing']; // No longer needed


    if (!speedEntity || speedEntity.state === 'unavailable' ||
        !throwTypeEntity || throwTypeEntity.state === 'unavailable' ||
        !distanceEntity || distanceEntity.state === 'unavailable') {
      content.innerHTML = '<div class="unavailable">No throw data available</div>';
      return;
    }

    const metricsTopRow = [
      {
        value: speedEntity.state,
        unit: 'mph',
        label: 'Speed'
      },
      {
        value: rotationEntity?.state || 'N/A',
        unit: 'rpm',
        label: 'Spin'
      },
      {
        value: wobbleEntity?.state || 'N/A',
        unit: '°',
        label: 'Wobble'
      }
    ];

    const metricsBottomRow = [
      {
        value: hyzerEntity?.state || 'N/A',
        unit: '°',
        label: 'Hyzer'
      },
      {
        value: noseEntity?.state || 'N/A',
        unit: '°',
        label: 'Nose'
      },
      {
        value: launchAngleEntity?.state || 'N/A',
        unit: '°',
        label: 'Launch'
      }
    ];

    const metricsTopRowHtml = metricsTopRow.map(metric => `
      <div class="metric">
        <div class="metric-label">${metric.label}</div>
        <div class="metric-value-container">
          <span class="metric-value">${metric.value}</span>
          <span class="metric-unit">${metric.unit}</span>
        </div>
      </div>
    `).join('');

    const metricsBottomRowHtml = metricsBottomRow.map(metric => `
      <div class="metric">
        <div class="metric-label">${metric.label}</div>
        <div class="metric-value-container">
          <span class="metric-value">${metric.value}</span>
          <span class="metric-unit">${metric.unit}</span>
        </div>
      </div>
    `).join('');

    // Get throw_time and bearing from attributes of throwTypeEntity
    let formattedThrowTime = 'N/A';
    const throwTimeSeconds = throwTypeEntity.attributes?.throw_time;

    if (throwTimeSeconds !== undefined && throwTimeSeconds !== null) {
        try {
            // throw_time is in seconds, Date constructor expects milliseconds
            const date = new Date(throwTimeSeconds * 1000);
            formattedThrowTime = date.toLocaleString(undefined, {
                weekday: 'long', hour: 'numeric', minute: 'numeric'
            });
        } catch (e) {
            _LOGGER.error("Error formatting throw time:", e);
            formattedThrowTime = 'Error'; // Or some other indicator
        }
    }

    const bearingAttribute = throwTypeEntity.attributes?.bearing;
    const bearingValue = bearingAttribute !== undefined && bearingAttribute !== null ? `${Math.round(parseFloat(bearingAttribute))}°` : null;

    let bearingHtml = '';
    if (bearingValue) {
      bearingHtml = `<span class="MuiStack-root css-14qay1w">Bearing: ${bearingValue}</span>`;
    }

    const distanceValue = distanceEntity && distanceEntity.state !== 'unavailable' && distanceEntity.state !== 'unknown'
      ? `${Math.round(parseFloat(distanceEntity.state))} ft`
      : 'N/A';

    content.innerHTML = `
      <div class="content-wrapper">
        <div class="left-column">
          <p class="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom css-ftrrzr">Latest Throw</p>
          <span class="MuiStack-root css-1ptfqyl">${throwTypeEntity.state || 'N/A'}</span>
          ${bearingHtml}
          <span class="MuiStack-root css-14qay1w">Time: ${formattedThrowTime}</span>
          <span class="MuiStack-root css-14qay1w">Distance: ${distanceValue}</span>
        </div>
        <div class="right-grid">
          ${metricsTopRowHtml}
          ${metricsBottomRowHtml}
        </div>
      </div>
    `;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('techdisc-card', TechDiscCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'techdisc-card',
  name: 'TechDisc Card',
  description: 'A card to display TechDisc throw metrics'
});
