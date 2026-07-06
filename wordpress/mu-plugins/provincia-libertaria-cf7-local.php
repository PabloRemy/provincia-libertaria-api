<?php
/**
 * Plugin Name: Provincia Libertaria CF7 Local
 * Description: Fuerza CF7 local sin correo y envia reportes a la API de pruebas.
 */

if (!defined('ABSPATH')) {
    exit;
}

add_filter('wpcf7_skip_mail', '__return_true');

add_action('rest_api_init', function () {
    register_rest_route('provincia-libertaria/v1', '/cf7-local', array(
        'methods' => 'GET',
        'callback' => function () {
            return array(
                'ok' => true,
                'plugin' => 'provincia-libertaria-cf7-local',
                'webhook' => 'http://api-test.local:8000/incidente-foto-json',
            );
        },
        'permission_callback' => '__return_true',
    ));
});

function pl_cf7_scalar($value) {
    if (is_array($value)) {
        $value = reset($value);
    }

    return is_scalar($value) ? (string) $value : '';
}

function pl_cf7_first_file_path($value) {
    if (is_array($value)) {
        foreach ($value as $item) {
            $path = pl_cf7_first_file_path($item);
            if ($path !== '') {
                return $path;
            }
        }

        return '';
    }

    return is_string($value) ? $value : '';
}

function pl_cf7_foto_payload($submission) {
    $uploaded_files = $submission->uploaded_files();

    $foto_path = '';
    if (isset($uploaded_files['foto'])) {
        $foto_path = pl_cf7_first_file_path($uploaded_files['foto']);
    }

    if ($foto_path === '' && isset($_FILES['foto']['tmp_name'])) {
        $foto_path = pl_cf7_first_file_path($_FILES['foto']['tmp_name']);
    }

    if ($foto_path === '') {
        error_log('Provincia Libertaria CF7 local foto ausente. uploaded_files=' . print_r($uploaded_files, true) . ' files=' . print_r($_FILES, true));
        return '';
    }

    if (!$foto_path || !is_readable($foto_path)) {
        error_log('Provincia Libertaria CF7 local foto no legible: ' . $foto_path . ' uploaded_files=' . print_r($uploaded_files, true) . ' files=' . print_r($_FILES, true));
        return '';
    }

    error_log('Provincia Libertaria CF7 local foto legible: ' . basename($foto_path) . ' bytes=' . filesize($foto_path));

    return array(
        'filename' => basename($foto_path),
        'content' => base64_encode(file_get_contents($foto_path)),
    );
}

function pl_cf7_enviar_webhook($data, $submission) {
    if (empty($data['ciudad']) || empty($data['categoria']) || empty($data['descripcion'])) {
        return;
    }

    $foto = pl_cf7_foto_payload($submission);

    $payload = array(
        'ciudad' => isset($data['ciudad']) ? pl_cf7_scalar($data['ciudad']) : '',
        'barrio' => isset($data['barrio']) ? pl_cf7_scalar($data['barrio']) : '',
        'categoria' => isset($data['categoria']) ? pl_cf7_scalar($data['categoria']) : '',
        'descripcion' => isset($data['descripcion']) ? pl_cf7_scalar($data['descripcion']) : '',
        'direccion' => isset($data['direccion']) ? pl_cf7_scalar($data['direccion']) : '',
        'latitud' => isset($data['latitud']) ? pl_cf7_scalar($data['latitud']) : '',
        'longitud' => isset($data['longitud']) ? pl_cf7_scalar($data['longitud']) : '',
        'foto' => $foto,
    );

    $response = wp_remote_post(
        'http://api-test.local:8000/incidente-foto-json',
        array(
            'timeout' => 10,
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'body' => wp_json_encode($payload),
        )
    );

    if (is_wp_error($response)) {
        error_log('Provincia Libertaria CF7 local webhook error: ' . $response->get_error_message());
        return;
    }

    $status_code = wp_remote_retrieve_response_code($response);
    if ($status_code < 200 || $status_code >= 300) {
        error_log('Provincia Libertaria CF7 local webhook HTTP ' . $status_code . ': ' . wp_remote_retrieve_body($response));
    }
}

add_action('wpcf7_before_send_mail', function () {
    if (!class_exists('WPCF7_Submission')) {
        return;
    }

    $submission = WPCF7_Submission::get_instance();
    if (!$submission) {
        return;
    }

    pl_cf7_enviar_webhook($submission->get_posted_data(), $submission);
}, 10, 0);
