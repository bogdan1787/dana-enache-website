/**
 * geo-links.js — Geo-target Amazon and PayPal links based on visitor country.
 * Tags to use in HTML:
 *   data-amazon-asin="B0FSJNJ5SN"   → rewrites href to local Amazon store
 *   data-paypal-link="true"          → rewrites href to regional PayPal link
 */
(function () {
  const paypalLinks = {
    IE: 'https://www.paypal.com/ncp/payment/48JM22NWSS5K6',
    EU: 'https://www.paypal.com/ncp/payment/46R5YDYTA7SGA',
    WW: 'https://www.paypal.com/ncp/payment/Y8CN6WNB9DLKE',
  };
  const defaultPaypalLink = 'https://www.paypal.com/ncp/payment/HJGJMCQG6QKVJ';

  const europeanCountries = [
    'AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU',
    'IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE',
    'AL','AD','AM','AZ','BY','BA','GE','IS','LI','MK','MD','MC','ME',
    'NO','SM','RS','CH','TR','UA','GB','VA',
  ];

  const amazonDomains = {
    US: 'amazon.com',    GB: 'amazon.co.uk', IE: 'amazon.ie',
    DE: 'amazon.de',     FR: 'amazon.fr',    IT: 'amazon.it',
    ES: 'amazon.es',     NL: 'amazon.nl',    SE: 'amazon.se',
    PL: 'amazon.pl',     AE: 'amazon.ae',    SA: 'amazon.sa',
    EG: 'amazon.eg',     TR: 'amazon.com.tr',SG: 'amazon.sg',
    CA: 'amazon.ca',     JP: 'amazon.co.jp', IN: 'amazon.in',
    AU: 'amazon.com.au', BR: 'amazon.com.br',MX: 'amazon.com.mx',
  };
  const defaultDomain = 'amazon.com';

  function updateLinks(country) {
    // Amazon
    document.querySelectorAll('a[data-amazon-asin]').forEach(a => {
      const asin   = a.dataset.amazonAsin;
      const domain = amazonDomains[country] || defaultDomain;
      a.href = `https://www.${domain}/dp/${asin}`;
    });
    // PayPal
    document.querySelectorAll('a[data-paypal-link]').forEach(a => {
      let link = paypalLinks.WW;
      if (country === 'IE')                         link = paypalLinks.IE;
      else if (europeanCountries.includes(country)) link = paypalLinks.EU;
      a.href = link;
    });
  }

  function fromBrowserLanguage() {
    const lang = navigator.language || '';
    return (lang.split('-')[1] || 'XX').toUpperCase();
  }

  function init() {
    const hasLinks =
      document.querySelector('a[data-amazon-asin]') ||
      document.querySelector('a[data-paypal-link]');
    if (!hasLinks) return;

    const run = () => {
      fetch('https://api.country.is/')
        .then(r => r.json())
        .then(d => { if (d && d.country) updateLinks(d.country); else updateLinks(fromBrowserLanguage()); })
        .catch(() =>
          fetch('https://get.geojs.io/v1/ip/country.json')
            .then(r => r.json())
            .then(d => { if (d && d.country) updateLinks(d.country); else updateLinks(fromBrowserLanguage()); })
            .catch(() => updateLinks(fromBrowserLanguage()))
        );
    };

    'requestIdleCallback' in window ? requestIdleCallback(run) : setTimeout(run, 0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
