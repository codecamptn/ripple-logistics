const map = L.map("map").setView([13.0475, 80.2090], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);


// ===============================
// DELIVERY DATA
// ===============================

const deliveries = [
    { id: "D1", name: "Hospital A", lat: 13.0105, lng: 80.2209, priority: "P3" },
    { id: "D2", name: "Pharmacy A", lat: 13.0250, lng: 80.2150, priority: "P2" },
    { id: "D3", name: "Retail A", lat: 13.0400, lng: 80.2100, priority: "P1" },

    { id: "D4", name: "Hospital B", lat: 13.0550, lng: 80.2250, priority: "P3" },
    { id: "D5", name: "Pharmacy B", lat: 13.0700, lng: 80.2350, priority: "P2" },
    { id: "D6", name: "Retail B", lat: 13.0850, lng: 80.2450, priority: "P1" },

    { id: "D7", name: "Hospital C", lat: 13.0200, lng: 80.2500, priority: "P3" },
    { id: "D8", name: "Retail C", lat: 13.0350, lng: 80.2600, priority: "P1" },

    { id: "D9", name: "Pharmacy C", lat: 13.0600, lng: 80.2000, priority: "P2" },
    { id: "D10", name: "Retail D", lat: 13.0750, lng: 80.1900, priority: "P1" },

    { id: "D11", name: "Hospital D", lat: 13.0450, lng: 80.1750, priority: "P3" },
    { id: "D12", name: "Pharmacy D", lat: 13.0600, lng: 80.1700, priority: "P2" },
    { id: "D13", name: "Retail E", lat: 13.0750, lng: 80.1650, priority: "P1" }
];


// ===============================
// VEHICLE ROUTES
// ===============================

const routes = {
    V1: ["D1", "D2", "D3"],
    V2: ["D4", "D5", "D6"],
    V3: ["D7", "D8", "D9", "D10"],
    V4: ["D11", "D12", "D13"]
};


// ===============================
// DEPOT
// ===============================

const depot = {
    name: "Guindy Depot",
    lat: 13.0067,
    lng: 80.2206
};


// Depot marker
L.marker([depot.lat, depot.lng])
    .addTo(map)
    .bindPopup(`
        <b>Guindy Depot</b><br>
        Main Logistics Depot
    `);


// ===============================
// DELIVERY MARKERS
// ===============================

const markerColors = {
    P3: "#d64545",
    P2: "#d99b21",
    P1: "#22a06b"
};

const deliveryMarkers = {};

deliveries.forEach(delivery => {

    const marker = L.circleMarker(
        [delivery.lat, delivery.lng],
        {
            radius: 7,
            color: "#ffffff",
            weight: 2,
            fillColor: "#22a06b",
            fillOpacity: 1
        }
    ).addTo(map);

    marker.bindPopup(`
        <b>${delivery.id}</b><br>
        ${delivery.name}<br>
        Priority: ${delivery.priority}
    `);

    deliveryMarkers[delivery.id] = marker;
});


// ===============================
// DRAW VEHICLE ROUTES
// ===============================

const routeLines = {};

Object.entries(routes).forEach(([vehicle, stopIds]) => {

    const points = [
        [depot.lat, depot.lng]
    ];

    stopIds.forEach(stopId => {

        const stop = deliveries.find(
            delivery => delivery.id === stopId
        );

        if (stop) {
            points.push([stop.lat, stop.lng]);
        }

    });

    // Return to depot
    points.push([depot.lat, depot.lng]);


    const line = L.polyline(
        points,
        {
            weight: 4,
            opacity: 0.8
        }
    ).addTo(map);

    line.bindTooltip(vehicle);

    routeLines[vehicle] = line;
});


// ===============================
// FIT MAP TO ROUTES
// ===============================

const allPoints = [
    [depot.lat, depot.lng],
    ...deliveries.map(d => [d.lat, d.lng])
];

map.fitBounds(allPoints);