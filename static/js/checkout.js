(() => {
  const dataNode = document.getElementById("delivery-data");
  if (!dataNode) return;
  const data = JSON.parse(dataNode.textContent);
  const form = document.querySelector(".order-form");
  const wilayaSelect = document.getElementById("wilaya-select");
  const communeSelect = document.getElementById("commune-select");
  const wilayaInput = document.getElementById("id_wilaya_id");
  const communeInput = document.getElementById("id_commune_id");
  const hubInput = document.getElementById("id_hub_id");
  const hubField = document.getElementById("pickup-hub-field");
  const hubSelect = document.getElementById("pickup-hub-select");
  const productPrice = Number(form.dataset.productPrice);
  const format = value => `${new Intl.NumberFormat("fr-DZ").format(value)} DA`;

  data.wilayas.forEach(item => {
    const option = new Option(`${String(item.code).padStart(2, "0")} — ${item.name}`, item.id);
    wilayaSelect.add(option);
  });

  const pricesFor = (communeId, wilayaId) => data.rates[communeId] || data.rates[wilayaId] || [];
  const selectedDeliveryType = () => form.querySelector("input[name='delivery_type']:checked")?.value || "home";

  function availableHubs() {
    return data.hubs.filter(item => item.address.districtTerritoryId === communeSelect.value || item.address.cityTerritoryId === wilayaSelect.value);
  }

  function updateHubs() {
    const hubs = availableHubs();
    const previous = hubInput.value;
    hubSelect.innerHTML = '<option value="">Choisir le point relais</option>';
    hubs.forEach(item => hubSelect.add(new Option(`${item.name}${item.address.street ? ` — ${item.address.street}` : ""}`, item.id)));
    if (hubs.some(item => item.id === previous)) hubSelect.value = previous;
    else hubInput.value = "";
    hubField.hidden = selectedDeliveryType() !== "pickup-point";
  }

  function updatePrices() {
    const prices = pricesFor(communeSelect.value, wilayaSelect.value);
    document.querySelectorAll("[data-rate]").forEach(node => {
      const item = prices.find(price => price.deliveryType === node.dataset.rate);
      node.textContent = item ? format(Math.round(item.price)) : "Indisponible";
      const radio = node.closest("label").querySelector("input");
      radio.disabled = !item || (node.dataset.rate === "pickup-point" && availableHubs().length === 0);
    });
    const current = prices.find(price => price.deliveryType === selectedDeliveryType());
    document.getElementById("delivery-price").textContent = current ? format(Math.round(current.price)) : "À calculer";
    document.getElementById("total-price").textContent = format(productPrice + (current ? Math.round(current.price) : 0));
  }

  function populateCommunes(wilayaId, selected = "") {
    communeSelect.innerHTML = '<option value="">Choisir la commune</option>';
    data.communes.filter(item => item.parentId === wilayaId).forEach(item => communeSelect.add(new Option(item.name, item.id)));
    communeSelect.disabled = !wilayaId;
    communeSelect.value = selected;
    wilayaInput.value = wilayaId;
    communeInput.value = selected;
    updateHubs();
    updatePrices();
  }

  wilayaSelect.addEventListener("change", () => populateCommunes(wilayaSelect.value));
  communeSelect.addEventListener("change", () => { communeInput.value = communeSelect.value; updateHubs(); updatePrices(); });
  hubSelect.addEventListener("change", () => { hubInput.value = hubSelect.value; });
  form.querySelectorAll("input[name='delivery_type']").forEach(input => input.addEventListener("change", () => { updateHubs(); updatePrices(); }));
  document.querySelectorAll(".thumbnail").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll(".thumbnail").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    document.getElementById("main-product-image").src = button.dataset.image;
  }));

  if (wilayaInput.value) {
    wilayaSelect.value = wilayaInput.value;
    populateCommunes(wilayaInput.value, communeInput.value);
  }
})();
