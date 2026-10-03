document.addEventListener("DOMContentLoaded", () => {
  const dateInput = document.querySelector('input[name="booking_date"]');
  if (dateInput && !dateInput.min) {
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    dateInput.min = local;
  }
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"], button:not([type])');
      if (button && !button.disabled && form.checkValidity()) {
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Please wait';
      }
    });
  });
});
