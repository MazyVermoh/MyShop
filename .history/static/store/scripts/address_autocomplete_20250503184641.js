// static/store/scripts/address_autocomplete.js
//   ПОДСТАВЬ свой публичный JS‑ключ DaData вместо XXX...
(function ($) {
    const token = "852cd2797dfa7726a7bcc6b792d862c38735b269";
  
    const opts = { token, type: "ADDRESS", language: "ru", count: 10 };
  
    // — город —
    $("#id_city").suggestions({
      ...opts,
      restrict_value: true,
      bounds: "city",
      onSelect: s => {
        if (s.data.country_iso_code) $("#id_country").val(s.data.country_iso_code);
        if (!$("#id_postcode").val() && s.data.postal_code)
          $("#id_postcode").val(s.data.postal_code);
      }
    });
  
    // — индекс (не обяз.) —
    $("#id_postcode").suggestions({
      ...opts,
      bounds: "postal_code"
    });
  
    // — улица / дом / кв. —
    $("#id_address").suggestions({
      ...opts,
      bounds: "street-house",
      constraints: $("#id_city"),
      onSelect: s => {
        if (!$("#id_postcode").val() && s.data.postal_code)
          $("#id_postcode").val(s.data.postal_code);
      }
    });
  })(jQuery);