const channelToneMap = {
  nominal: 220,
  advisory: 246.94,
  warning: 293.66,
  critical: 349.23,
  recovery: 261.63,
  opportunity: 329.63,
  handoff: 392.0
};

function formatState(signal) {
  return `V ${signal.valence.toFixed(2)} / E ${signal.energy.toFixed(2)} / T ${signal.tension.toFixed(2)}`;
}

function formatRenderHints(signal) {
  return `I ${signal.intensity.toFixed(2)} / H ${signal.hue.toFixed(0)} / P ${signal.pulse.toFixed(2)}`;
}

function bindSignal(signal) {
  document.getElementById("occurredAt").textContent = signal.occurred_at;
  document.getElementById("producer").textContent = signal.producer;
  document.getElementById("entity").textContent = signal.entity;
  document.getElementById("event").textContent = signal.event;
  document.getElementById("channel").textContent = signal.channel;
  document.getElementById("state").textContent = formatState(signal);
  document.getElementById("renderHints").textContent = formatRenderHints(signal);
}

async function playEarcon(signal) {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return;

  const context = new AudioContextClass();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const filter = context.createBiquadFilter();

  oscillator.type = signal.channel === "warning" || signal.channel === "critical" ? "sawtooth" : "sine";
  oscillator.frequency.value = channelToneMap[signal.channel] ?? 220;
  filter.type = "lowpass";
  filter.frequency.value = 900 + signal.intensity * 1400 + signal.pulse * 180;

  gain.gain.setValueAtTime(0.0001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(Math.max(0.02, signal.intensity * 0.16), context.currentTime + 0.03);
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.52);

  oscillator.connect(filter);
  filter.connect(gain);
  gain.connect(context.destination);

  oscillator.start();
  oscillator.stop(context.currentTime + 0.56);

  await new Promise((resolve) => setTimeout(resolve, 650));
  await context.close();
}

async function main() {
  const response = await fetch("./sample-signal.json");
  const signal = await response.json();
  bindSignal(signal);
  document.getElementById("play").addEventListener("click", () => {
    void playEarcon(signal);
  });
}

void main();
