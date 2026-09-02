(function () {
  "use strict";

  const script = document.currentScript;
  if (!script) return;

  const scriptUrl = new URL(script.src);
  const widgetId = scriptUrl.searchParams.get("id");
  if (!widgetId) {
    console.error("Widget public id is missing");
    return;
  }

  const apiOrigin = scriptUrl.origin;
  const host = document.createElement("div");
  host.setAttribute("data-flyrank-widget", widgetId);
  host.style.cssText = "max-width:420px;padding:20px;border:1px solid #d0d7de;border-radius:12px;font-family:Arial,sans-serif;background:#fff;color:#1f2328";
  script.insertAdjacentElement("afterend", host);

  fetch(`${apiOrigin}/public/widgets/${encodeURIComponent(widgetId)}/config`)
    .then((response) => {
      if (!response.ok) throw new Error(`Config request failed (${response.status})`);
      return response.json();
    })
    .then(render)
    .catch((error) => {
      host.textContent = "The contact form is temporarily unavailable.";
      console.error(error);
    });

  function render(config) {
    const title = document.createElement("h2");
    title.textContent = config.title;
    host.appendChild(title);

    if (config.description) {
      const description = document.createElement("p");
      description.textContent = config.description;
      host.appendChild(description);
    }

    const form = document.createElement("form");
    form.noValidate = true;

    config.fields.forEach((field) => {
      const label = document.createElement("label");
      label.textContent = field.label;
      label.style.cssText = "display:block;margin:12px 0 4px;font-weight:600";
      const input = field.type === "textarea" ? document.createElement("textarea") : document.createElement("input");
      if (field.type !== "textarea") input.type = field.type;
      input.name = field.name;
      input.required = field.required;
      input.style.cssText = "box-sizing:border-box;width:100%;padding:9px;border:1px solid #8c959f;border-radius:6px";
      label.appendChild(input);
      form.appendChild(label);
    });

    const honeypot = document.createElement("input");
    honeypot.name = "company_website";
    honeypot.tabIndex = -1;
    honeypot.autocomplete = "off";
    honeypot.setAttribute("aria-hidden", "true");
    honeypot.style.display = "none";
    form.appendChild(honeypot);

    const button = document.createElement("button");
    button.type = "submit";
    button.textContent = config.button_text;
    button.style.cssText = "margin-top:14px;padding:10px 18px;border:0;border-radius:6px;background:#0969da;color:#fff;cursor:pointer";
    form.appendChild(button);

    const result = document.createElement("p");
    result.setAttribute("role", "status");
    form.appendChild(result);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      result.textContent = "Sending...";
      const values = Object.fromEntries(new FormData(form).entries());
      const idempotencyKey = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
      try {
        const response = await fetch(config.submission_url, {
          method: "POST",
          headers: {"Content-Type": "application/json", "Idempotency-Key": idempotencyKey},
          body: JSON.stringify(values),
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.detail || body.error || "Submission failed");
        result.textContent = "Thank you. Your message was received.";
        form.reset();
      } catch (error) {
        result.textContent = error.message;
      } finally {
        button.disabled = false;
      }
    });

    host.appendChild(form);
  }
})();
