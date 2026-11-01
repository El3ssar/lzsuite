/* Replace the mobile label with a native keyboard-accessible button. */
(() => {
  const label = document.querySelector('.md-header label[for="__drawer"]');
  const drawer = document.querySelector("#__drawer");
  const navigation = document.querySelector(".md-nav--primary");
  if (!label || !drawer || !navigation) return;

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = label.className;
  trigger.innerHTML = label.innerHTML;
  trigger.setAttribute("data-navigation-toggle", "");
  navigation.id = "documentation-navigation";
  trigger.setAttribute("aria-controls", navigation.id);
  label.replaceWith(trigger);

  const update = () => {
    trigger.setAttribute("aria-expanded", String(drawer.checked));
    trigger.setAttribute(
      "aria-label",
      drawer.checked ? "Close navigation" : "Open navigation",
    );
  };
  drawer.addEventListener("change", update);
  trigger.addEventListener("click", () => {
    drawer.checked = !drawer.checked;
    drawer.dispatchEvent(new Event("change", { bubbles: true }));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && drawer.checked) {
      drawer.checked = false;
      drawer.dispatchEvent(new Event("change", { bubbles: true }));
      trigger.focus();
    }
  });
  update();
})();
