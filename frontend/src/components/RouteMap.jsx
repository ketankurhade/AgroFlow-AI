import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export const RouteMap = ({ stops = [], height = "400px" }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize Leaflet map if not already initialized
    if (!mapInstanceRef.current) {
      // Center default on Maharashtra region (Pune/Mumbai coordinates)
      const map = L.map(mapRef.current, {
        center: [18.8, 73.8],
        zoom: 7,
        scrollWheelZoom: false,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupRef.current = L.layerGroup().addTo(map);
    }

    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;

    layerGroup.clearLayers();

    if (!stops || stops.length === 0) return;

    const latLngs = [];

    stops.forEach((stop, idx) => {
      const lat = stop.latitude;
      const lng = stop.longitude;
      if (lat == null || lng == null) return;

      const position = [lat, lng];
      latLngs.push(position);

      const isStart = idx === 0;
      const markerHtml = `
        <div style="
          background-color: ${isStart ? '#059669' : '#2563eb'};
          color: white;
          width: 30px;
          height: 30px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 13px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.3);
          border: 2px solid white;
        ">
          ${idx + 1}
        </div>
      `;

      const customIcon = L.divIcon({
        html: markerHtml,
        className: 'custom-stop-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const popupContent = `
        <div style="font-family: sans-serif; font-size: 12px; padding: 2px;">
          <div style="font-weight: bold; color: #0f172a; font-size: 13px;">Stop ${idx + 1}: ${stop.name}</div>
          <div style="color: #64748b; margin-top: 2px;">City: ${stop.city || 'AgroFlow Hub'}</div>
          <div style="color: #059669; font-weight: 600; margin-top: 4px;">
            ${isStart ? '🚀 Starting Depot' : `Leg Visit #${idx + 1}`}
          </div>
          <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">
            Coords: ${lat.toFixed(4)}, ${lng.toFixed(4)}
          </div>
        </div>
      `;

      L.marker(position, { icon: customIcon })
        .bindPopup(popupContent)
        .addTo(layerGroup);
    });

    if (latLngs.length >= 2) {
      const polyline = L.polyline(latLngs, {
        color: '#059669',
        weight: 4,
        opacity: 0.85,
        dashArray: '8, 8',
      }).addTo(layerGroup);

      map.fitBounds(polyline.getBounds().pad(0.2));
    } else if (latLngs.length === 1) {
      map.setView(latLngs[0], 10);
    }
  }, [stops]);

  return (
    <div className="relative rounded-xl overflow-hidden border border-slate-200/80 shadow-xs">
      <div ref={mapRef} style={{ height: height, width: '100%', zIndex: 1 }} />
      <div className="absolute bottom-2 right-2 z-10 bg-white/90 backdrop-blur-xs px-3 py-1 rounded-md border border-slate-200 text-[10px] text-slate-600 font-medium">
        📍 Visual geographic route path (straight line segments). Not live GPS tracking.
      </div>
    </div>
  );
};
