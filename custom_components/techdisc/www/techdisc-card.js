class TechDiscCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
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
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 12px;
        }
        .metric {
          background: var(--secondary-background-color);
          border-radius: 8px;
          padding: 12px;
          text-align: center;
        }
        .metric-value {
          font-size: 1.4em;
          font-weight: bold;
          color: var(--primary-color);
          margin-bottom: 4px;
        }
        .metric-label {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .metric-unit {
          font-size: 0.8em;
          color: var(--secondary-text-color);
        }
        .throw-info {
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
    const distanceEntity = this._hass.states['sensor.techdisc_distance'];
    const hyzerEntity = this._hass.states['sensor.techdisc_hyzer_angle'];
    const noseEntity = this._hass.states['sensor.techdisc_nose_angle'];
    const rotationEntity = this._hass.states['sensor.techdisc_rotation'];
    const launchAngleEntity = this._hass.states['sensor.techdisc_launch_angle'];
    const wobbleEntity = this._hass.states['sensor.techdisc_wobble'];
    const throwTypeEntity = this._hass.states['sensor.techdisc_throw_type'];

    if (!speedEntity || speedEntity.state === 'unavailable') {
      content.innerHTML = '<div class="unavailable">No throw data available</div>';
      return;
    }

    const metrics = [
      {
        value: speedEntity.state,
        unit: 'mph',
        label: 'Speed'
      },
      {
        value: distanceEntity?.state || 'N/A',
        unit: 'ft',
        label: 'Distance'
      },
      {
        value: hyzerEntity?.state || 'N/A',
        unit: '°',
        label: 'Hyzer Angle'
      },
      {
        value: noseEntity?.state || 'N/A',
        unit: '°',
        label: 'Nose Angle'
      },
      {
        value: launchAngleEntity?.state || 'N/A',
        unit: '°',
        label: 'Launch Angle'
      },
      {
        value: rotationEntity?.state || 'N/A',
        unit: 'rpm',
        label: 'Rotation'
      },
      {
        value: wobbleEntity?.state || 'N/A',
        unit: '°',
        label: 'Wobble'
      }
    ];

    const metricsHtml = metrics.map(metric => `
      <div class="metric">
        <div class="metric-value">
          ${metric.value}
          <span class="metric-unit">${metric.unit}</span>
        </div>
        <div class="metric-label">${metric.label}</div>
      </div>
    `).join('');

    const throwInfo = throwTypeEntity ? `
      <div class="throw-info">
        <div class="throw-type">${throwTypeEntity.state}</div>
        <div class="throw-details">
          ${throwTypeEntity.attributes.handedness ? `<div>Hand: ${throwTypeEntity.attributes.handedness}</div>` : ''}
          ${throwTypeEntity.attributes.temperature ? `<div>Temp: ${Math.round(throwTypeEntity.attributes.temperature)}°C</div>` : ''}
          ${throwTypeEntity.attributes.bearing ? `<div>Bearing: ${Math.round(throwTypeEntity.attributes.bearing)}°</div>` : ''}
          ${throwTypeEntity.attributes.uphill_angle ? `<div>Uphill: ${Math.round(throwTypeEntity.attributes.uphill_angle)}°</div>` : ''}
        </div>
      </div>
    ` : '';

    content.innerHTML = `
      <div class="metrics-grid">
        ${metricsHtml}
      </div>
      ${throwInfo}
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
