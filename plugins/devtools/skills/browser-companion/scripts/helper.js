/*
 * arkhe-preview helper (generic) — runs in the browser.
 *
 * Default behavior:
 *   - Open WebSocket to the current page's host/port
 *   - On {type:'reload'}, reload the page
 *   - Capture clicks on any element with a [data-event] attribute and ship
 *     the event over WS as {type:'click', action, payload}
 *   - Queue events while WS is disconnected and flush on reconnect
 *   - Reconnect with exponential backoff (1s, 2s, 4s, ..., max 30s)
 *
 * Consumers that want richer UI (indicator bars, multi-select tracking, gallery
 * variant switching, etc.) should ship their own helper file and pass it via
 *   arkhe-preview start --helper <path>
 *
 * Derived in spirit from the superpowers project (MIT, Jesse Vincent 2025).
 */
(function () {
  const WS_URL = 'ws://' + window.location.host;
  let ws = null;
  let queue = [];
  let backoff = 1000;

  function connect() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      backoff = 1000; // reset
      while (queue.length > 0) {
        ws.send(JSON.stringify(queue.shift()));
      }
    };

    ws.onmessage = (msg) => {
      let data;
      try { data = JSON.parse(msg.data); } catch (_) { return; }
      if (data.type === 'reload') {
        window.location.reload();
      }
    };

    ws.onclose = () => {
      ws = null;
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, 30000);
    };

    ws.onerror = () => {
      try { ws.close(); } catch (_) {}
    };
  }

  function sendEvent(event) {
    if (!event.timestamp) event.timestamp = Date.now();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(event));
    } else {
      queue.push(event);
    }
  }

  // Generic click capture: any element with [data-event] is reportable.
  // Payload is the bag of all other data-* attributes (excluding `event`).
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-event]');
    if (!target) return;

    const payload = {};
    for (const attr of target.attributes) {
      if (attr.name.startsWith('data-') && attr.name !== 'data-event') {
        // strip the "data-" prefix for cleaner JSON
        payload[attr.name.slice(5)] = attr.value;
      }
    }

    sendEvent({
      type: 'click',
      action: target.dataset.event,
      payload,
      text: target.textContent.trim().slice(0, 200),
      id: target.id || null
    });
  });

  // Public API for explicit programmatic sends:
  //   window.arkhePreview.send({ type: 'custom', ... })
  window.arkhePreview = {
    send: sendEvent
  };

  connect();
})();
