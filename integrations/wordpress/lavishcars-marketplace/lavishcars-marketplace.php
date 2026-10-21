<?php
/**
 * Plugin Name: LavishCars Marketplace Bridge (Concept)
 * Description: Public API catalog shortcode with links to the demonstration storefront. No marketplace records are stored in WordPress.
 * Version: 0.1.0
 * Requires PHP: 8.0
 * License: GPL-2.0-or-later
 */

if (!defined('ABSPATH')) {
    exit;
}

/** Server configuration only: never accept an API origin from shortcode or query input. */
function lavishcars_bridge_origin(string $constant): string {
    if (!defined($constant)) {
        return '';
    }
    $value = rtrim((string) constant($constant), '/');
    $parts = wp_parse_url($value);
    if (!$parts || empty($parts['host']) || !in_array($parts['scheme'] ?? '', ['http', 'https'], true)
        || isset($parts['user']) || isset($parts['pass']) || isset($parts['query']) || isset($parts['fragment'])) {
        return '';
    }
    return $value;
}

function lavishcars_bridge_catalog($attributes): string {
    $api = lavishcars_bridge_origin('LAVISHCARS_API_ORIGIN');
    $storefront = lavishcars_bridge_origin('LAVISHCARS_STOREFRONT_ORIGIN');
    if (!$api || !$storefront) {
        return '<p role="status">The demonstration catalog has not been configured.</p>';
    }
    $attributes = shortcode_atts(['city' => '', 'category' => '', 'limit' => '6'], $attributes, 'lavishcars_catalog');
    $query = ['page' => 1, 'page_size' => min(12, max(1, absint($attributes['limit'])))];
    foreach (['city', 'category'] as $field) {
        if ($attributes[$field] !== '') {
            $query[$field] = substr(sanitize_text_field($attributes[$field]), 0, 80);
        }
    }
    // No response caching: suspension and moderation should take effect on the next request.
    // An origin is explicitly configured by the site operator; local origins support local demos.
    $response = wp_remote_get(add_query_arg($query, $api . '/api/v1/listings'), [
        'timeout' => 5,
        'redirection' => 0,
        'limit_response_size' => 256 * 1024,
        'headers' => ['Accept' => 'application/json'],
    ]);
    if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) {
        return '<p role="status">The demonstration catalog is temporarily unavailable. Please try again later.</p>';
    }
    $payload = json_decode(wp_remote_retrieve_body($response), true);
    if (!is_array($payload) || !isset($payload['items']) || !is_array($payload['items'])) {
        return '<p role="status">The demonstration catalog could not be loaded.</p>';
    }
    $html = '<section class="lavishcars-bridge" aria-label="Demonstration vehicle catalog">';
    $html .= '<p class="lavishcars-bridge-note">Unofficial concept · Synthetic inventory and illustrative prices. Availability must be confirmed by the supplier.</p>';
    $html .= '<div class="lavishcars-bridge-grid">';
    $count = 0;
    foreach (array_slice($payload['items'], 0, $query['page_size']) as $listing) {
        if (!is_array($listing) || empty($listing['slug']) || !is_string($listing['slug'])) {
            continue;
        }
        $title = is_string($listing['title'] ?? null) ? $listing['title'] : 'View vehicle';
        $currency = is_string($listing['currency'] ?? null) ? $listing['currency'] : '';
        $price = is_scalar($listing['daily_price'] ?? null) ? (string) $listing['daily_price'] : '';
        $city = is_string($listing['city'] ?? null) ? $listing['city'] : '';
        $url = $storefront . '/fleet/' . rawurlencode($listing['slug']);
        $html .= '<article class="lavishcars-bridge-card"><h3>' . esc_html($title) . '</h3>';
        $html .= '<p>' . esc_html($city) . '</p>';
        $html .= '<p>' . ($price !== '' ? esc_html($currency . ' ' . $price . ' / day') : 'Price on inquiry') . '</p>';
        $html .= '<a href="' . esc_url($url) . '">View vehicle &amp; request a quote<span class="screen-reader-text"> for ' . esc_html($title) . '</span></a></article>';
        $count++;
    }
    if ($count === 0) {
        $html .= '<p>No matching demonstration vehicles were found.</p>';
    }
    return $html . '</div></section>';
}
add_shortcode('lavishcars_catalog', 'lavishcars_bridge_catalog');


// Enqueue before wp_head: shortcodes may be rendered after the document head.
function lavishcars_bridge_styles(): void {
    wp_enqueue_style('lavishcars-bridge', plugins_url('catalog.css', __FILE__), [], '0.1.0');
}
add_action('wp_enqueue_scripts', 'lavishcars_bridge_styles');
