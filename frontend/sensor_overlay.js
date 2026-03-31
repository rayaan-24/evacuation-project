/**
 * sensor_overlay.js - Visual Sensor Overlay for Smart Evacuation System
 * 
 * Adds real-time sensor indicators on the building map that change color
 * based on sensor status. Integrates with the existing IoT simulation.
 * 
 * Usage: Include this file in smart_evacuation_demo.html after renderer.js
 */

class SensorOverlay {
    constructor(canvasId, layout) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.layout = layout;
        this.sensors = new Map();
        this.sensorStatuses = new Map();
        this.animationFrame = null;
        this.pulsePhase = 0;
        
        this.COLORS = {
            NORMAL: '#22c55e',      // Green
            FIRE: '#ff4444',        // Red
            SMOKE: '#f97316',       // Orange
            BLOCKAGE: '#3b82f6',    // Blue
            CROWD: '#fbbf24',       // Yellow
            GAS: '#a855f7',         // Purple
            UNKNOWN: '#6b7280'      // Gray
        };
        
        this.SENSOR_RADIUS = 4;
        this.PULSE_MAX_RADIUS = 8;
        this.PULSE_SPEED = 0.05;
    }
    
    init() {
        this.loadSensorMap();
        this.startAnimation();
        this.setupPolling();
        console.log('SensorOverlay initialized with', this.sensors.size, 'sensors');
    }
    
    loadSensorMap() {
        const sensorMap = this.layout.sensor_map || {};
        
        Object.entries(sensorMap).forEach(([sensorId, locationId]) => {
            const corridor = this.findCorridorById(locationId);
            if (corridor) {
                const centerX = corridor.x + corridor.w / 2;
                const centerY = corridor.y + corridor.h / 2;
                
                this.sensors.set(sensorId, {
                    id: sensorId,
                    locationId: locationId,
                    x: centerX,
                    y: centerY,
                    status: 'NORMAL',
                    type: null,
                    lastUpdate: null
                });
            }
        });
        
        console.log('Loaded sensor map:', this.sensors.size, 'sensors');
    }
    
    findCorridorById(corridorId) {
        const corridors = this.layout.corridors || [];
        return corridors.find(c => c.id === corridorId);
    }
    
    updateSensorStatus(sensorId, status, emergencyType = null) {
        const sensor = this.sensors.get(sensorId);
        if (sensor) {
            sensor.status = status;
            sensor.type = emergencyType;
            sensor.lastUpdate = Date.now();
            
            this.updateSensorPanel(sensorId, status, emergencyType);
        }
    }
    
    updateSensorPanel(sensorId, status, emergencyType) {
        const row = document.querySelector(`[data-sensor-id="${sensorId}"]`);
        if (!row) return;
        
        const dot = row.querySelector('.sdot');
        const value = row.querySelector('.sval');
        
        if (status === 'TRIGGERED' || status === 'ACTIVE') {
            const colorVar = emergencyType ? 
                (emergencyType === 'FIRE' ? 'fire' : 
                 emergencyType === 'SMOKE' ? 'smoke' :
                 emergencyType === 'GAS' ? 'gas' :
                 emergencyType === 'CROWD' ? 'crowd' : 'blue') : 'fire';
            
            dot.className = `sdot ${colorVar}`;
            value.style.color = `var(--${colorVar})`;
            value.textContent = `${emergencyType || 'ACTIVE'}!`;
        } else {
            dot.className = 'sdot safe';
            value.style.color = 'var(--green)';
            value.textContent = 'Normal';
        }
    }
    
    fetchSensorStatus() {
        return fetch('/sensor-status')
            .then(res => res.json())
            .then(data => {
                this.processSensorStatus(data);
            })
            .catch(err => {
                console.error('Error fetching sensor status:', err);
            });
    }
    
    processSensorStatus(data) {
        const activeEmergencies = data.active_emergencies || [];
        const activeSensorIds = new Set(activeEmergencies.map(e => e.sensor_id));
        
        this.sensors.forEach((sensor, sensorId) => {
            const emergency = activeEmergencies.find(e => e.sensor_id === sensorId);
            
            if (emergency) {
                sensor.status = 'ACTIVE';
                sensor.type = emergency.type;
                sensor.lastUpdate = Date.now();
            } else {
                sensor.status = 'NORMAL';
                sensor.type = null;
            }
            
            this.updateSensorPanel(sensorId, sensor.status, sensor.type);
        });
        
        const activeCount = document.getElementById('dbEmergencies');
        if (activeCount) {
            activeCount.textContent = activeEmergencies.length;
        }
    }
    
    setupPolling(interval = 2000) {
        this.pollInterval = setInterval(() => {
            this.fetchSensorStatus();
        }, interval);
        
        this.fetchSensorStatus();
    }
    
    startAnimation() {
        const animate = () => {
            this.pulsePhase += this.PULSE_SPEED;
            if (this.pulsePhase > Math.PI * 2) {
                this.pulsePhase = 0;
            }
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }
    
    stopAnimation() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
    }
    
    draw() {
        const VIEW = window.VIEW || { padding: 35, pixelsPerMeter: 14 };
        
        this.sensors.forEach((sensor, sensorId) => {
            const px = VIEW.padding + sensor.x * VIEW.pixelsPerMeter;
            const py = VIEW.padding + sensor.y * VIEW.pixelsPerMeter;
            
            let color = this.COLORS.NORMAL;
            let pulseRadius = 0;
            
            if (sensor.status === 'ACTIVE') {
                color = this.COLORS[sensor.type] || this.COLORS.FIRE;
                pulseRadius = this.PULSE_MAX_RADIUS * Math.abs(Math.sin(this.pulsePhase));
            }
            
            if (sensor.status === 'TRIGGERED') {
                color = this.COLORS[sensor.type] || this.COLORS.FIRE;
                pulseRadius = this.PULSE_MAX_RADIUS * Math.abs(Math.sin(this.pulsePhase));
            }
            
            if (pulseRadius > 0) {
                this.ctx.beginPath();
                this.ctx.arc(px, py, this.SENSOR_RADIUS + pulseRadius, 0, Math.PI * 2);
                this.ctx.fillStyle = this.hexToRgba(color, 0.3);
                this.ctx.fill();
            }
            
            this.ctx.beginPath();
            this.ctx.arc(px, py, this.SENSOR_RADIUS, 0, Math.PI * 2);
            this.ctx.fillStyle = color;
            this.ctx.fill();
            
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 1;
            this.ctx.stroke();
            
            this.ctx.fillStyle = '#fff';
            this.ctx.font = 'bold 6px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            const sensorNum = sensorId.replace('sensor_', '');
            this.ctx.fillText(sensorNum, px, py);
        });
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    getSensorAt(x, y) {
        const VIEW = window.VIEW || { padding: 35, pixelsPerMeter: 14 };
        
        for (const [sensorId, sensor] of this.sensors) {
            const px = VIEW.padding + sensor.x * VIEW.pixelsPerMeter;
            const py = VIEW.padding + sensor.y * VIEW.pixelsPerMeter;
            
            const distance = Math.sqrt(Math.pow(x - px, 2) + Math.pow(y - py, 2));
            
            if (distance <= this.SENSOR_RADIUS + 5) {
                return sensor;
            }
        }
        
        return null;
    }
    
    showSensorInfo(sensor) {
        const info = `
Sensor ID: ${sensor.id}
Location: ${sensor.locationId}
Status: ${sensor.status}
Type: ${sensor.type || 'N/A'}
Last Update: ${sensor.lastUpdate ? new Date(sensor.lastUpdate).toLocaleTimeString() : 'N/A'}
        `;
        console.log(info);
    }
}


window.SensorOverlay = SensorOverlay;
