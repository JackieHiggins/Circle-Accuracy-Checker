const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
const accuracyLabel = document.getElementById('accuracyLabel');
const bestAccuracyLabel = document.getElementById('bestAccuracyLabel');
const seeBestAttemptBtn = document.getElementById('seeBestAttemptBtn');

const MIN_RADIUS = 70;
const CLOSE_ENOUGH_THRESHOLD = 60;

let drawing = false;
let userPoints = [];
let bestAccuracy = 0;
let bestAttemptPoints = [];

function resizeCanvas() {
    canvas.width = window.innerWidth * 0.8;
    canvas.height = window.innerHeight * 0.8;
    drawCentralDot();
}

function drawCentralDot() {
    const center = { x: canvas.width / 2, y: canvas.height / 2 };
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(center.x, center.y, 2, 0, Math.PI * 2);
    ctx.fill();
}

function startDrawing(event) {
    drawing = true;
    userPoints = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCentralDot();
    addPoint(event);
}

function draw(event) {
    if (!drawing) return;
    addPoint(event);
    drawLine();
    const accuracy = calculateAccuracy();
    accuracyLabel.textContent = `${accuracy.toFixed(1)}%`;
    accuracyLabel.style.color = getColor(accuracy);
}

function stopDrawing() {
    drawing = false;
    const center = { x: canvas.width / 2, y: canvas.height / 2 };
    const averageRadius = calculateAverageRadius();
    if (averageRadius < MIN_RADIUS) {
        alert("The circle is too small. Please draw a larger circle.");
        accuracyLabel.textContent = '0.0%';
        accuracyLabel.style.color = 'white';
        return;
    }
    if (isCloseEnough(userPoints[0], userPoints[userPoints.length - 1])) {
        const accuracy = calculateAccuracy();
        accuracyLabel.textContent = `${accuracy.toFixed(1)}%`;
        if (accuracy > bestAccuracy) {
            bestAccuracy = accuracy;
            bestAccuracyLabel.textContent = `Best: ${accuracy.toFixed(1)}%`;
            bestAttemptPoints = [...userPoints];
        }
    } else {
        accuracyLabel.textContent = '0.0%';
        accuracyLabel.style.color = 'white';
    }
}

function addPoint(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    userPoints.push({ x, y });
}

function drawLine() {
    if (userPoints.length < 2) return;
    const accuracy = calculateAccuracy();
    ctx.strokeStyle = getColor(accuracy);
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(userPoints[userPoints.length - 2].x, userPoints[userPoints.length - 2].y);
    ctx.lineTo(userPoints[userPoints.length - 1].x, userPoints[userPoints.length - 1].y);
    ctx.stroke();
}

function isCloseEnough(point1, point2) {
    return Math.hypot(point2.x - point1.x, point2.y - point1.y) < CLOSE_ENOUGH_THRESHOLD;
}

function calculateAccuracy() {
    const center = { x: canvas.width / 2, y: canvas.height / 2 };
    const radii = userPoints.map(point => Math.hypot(point.x - center.x, point.y - center.y));
    const idealRadius = calculateAverageRadius();
    const averageDistance = radii.reduce((sum, r) => sum + Math.abs(idealRadius - r), 0) / radii.length;
    const stdDeviation = Math.sqrt(radii.reduce((sum, r) => sum + Math.pow(r - idealRadius, 2), 0) / radii.length);
    return Math.max(0, 100 - (averageDistance + stdDeviation));
}

function calculateAverageRadius() {
    const center = { x: canvas.width / 2, y: canvas.height / 2 };
    return userPoints.reduce((sum, point) => sum + Math.hypot(point.x - center.x, point.y - center.y), 0) / userPoints.length;
}

function getColor(accuracy) {
    const colors = [
        { r: 255, g: 0, b: 0 },       // Red
        { r: 255, g: 165, b: 0 },     // Orange
        { r: 255, g: 255, b: 0 },     // Yellow
        { r: 0, g: 255, b: 0 }        // Green
    ];
    const ranges = [60, 80, 90, 100];

    if (accuracy <= ranges[0]) {
        return `rgb(${colors[0].r}, ${colors[0].g}, ${colors[0].b})`;
    } else if (accuracy <= ranges[1]) {
        const ratio = (accuracy - ranges[0]) / (ranges[1] - ranges[0]);
        return interpolateColor(colors[0], colors[1], ratio);
    } else if (accuracy <= ranges[2]) {
        const ratio = (accuracy - ranges[1]) / (ranges[2] - ranges[1]);
        return interpolateColor(colors[1], colors[2], ratio);
    } else if (accuracy <= ranges[3]) {
        const ratio = (accuracy - ranges[2]) / (ranges[3] - ranges[2]);
        return interpolateColor(colors[2], colors[3], ratio);
    } else {
        return `rgb(${colors[3].r}, ${colors[3].g}, ${colors[3].b})`;
    }
}

function interpolateColor(color1, color2, ratio) {
    const r = Math.round(color1.r * (1 - ratio) + color2.r * ratio);
    const g = Math.round(color1.g * (1 - ratio) + color2.g * ratio);
    const b = Math.round(color1.b * (1 - ratio) + color2.b * ratio);
    return `rgb(${r}, ${g}, ${b})`;
}

function seeBestAttempt() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCentralDot();
    if (bestAttemptPoints.length === 0) return;
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(bestAttemptPoints[0].x, bestAttemptPoints[0].y);
    for (let i = 1; i < bestAttemptPoints.length; i++) {
        ctx.lineTo(bestAttemptPoints[i].x, bestAttemptPoints[i].y);
    }
    ctx.stroke();
}

window.addEventListener('resize', resizeCanvas);
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);

seeBestAttemptBtn.addEventListener('click', seeBestAttempt);

resizeCanvas();
drawCentralDot();
