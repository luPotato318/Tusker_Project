<?php
header('Content-Type: application/json; charset=utf-8');

class PiemApiBridge {
    private $piemApiUrl;
    private $supabaseUrl;
    private $supabaseKey;
    private $bridgeSecret;

    public function __construct() {
        $this->piemApiUrl = getenv('PIEM_API_URL') ?: 'http://localhost:8000';
        $this->supabaseUrl = getenv('SUPABASE_URL') ?: 'https://seu-projeto.supabase.co';
        $this->supabaseKey = getenv('SUPABASE_ANON_KEY') ?: 'sua_chave_anonima';
        $this->bridgeSecret = getenv('PHP_BRIDGE_SECRET') ?: '';
    }

    
    public function askTutor($mensagem, $area = "Tecnologia da Informação", $perfil = "external") {
        $url = rtrim($this->piemApiUrl, '/') . '/api/bridge/tutor/';
        
        $data = array(
            'mensagem' => $mensagem,
            'area' => $area,
            'perfil' => $perfil
        );

        $options = array(
            'http' => array(
                'header'  => "Content-Type: application/json\r\n" .
                             "X-PIEM-Bridge-Secret: {$this->bridgeSecret}\r\n",
                'method'  => 'POST',
                'content' => json_encode($data),
                'timeout' => 10
            )
        );

        $context  = stream_context_create($options);
        $result = @file_get_contents($url, false, $context);

        if ($result === FALSE) {
            return array(
                'status' => 'erro',
                'resposta_tutor' => 'Não foi possível conectar ao servidor Django/PIEM em PHP.'
            );
        }

        return json_decode($result, true);
    }

    
    public function getSupabaseProjects() {
        $url = rtrim($this->supabaseUrl, '/') . '/rest/v1/core_studentproject?publico=eq.true&select=*';

        $options = array(
            'http' => array(
                'header'  => "apikey: {$this->supabaseKey}\r\n" .
                             "Authorization: Bearer {$this->supabaseKey}\r\n" .
                             "Content-Type: application/json\r\n",
                'method'  => 'GET',
                'timeout' => 5
            )
        );

        $context  = stream_context_create($options);
        $result = @file_get_contents($url, false, $context);

        if ($result === FALSE) {
            return array('status' => 'erro', 'mensagem' => 'Falha na requisição ao Supabase em PHP.');
        }

        return json_decode($result, true);
    }
}

if (basename(__FILE__) == basename($_SERVER['SCRIPT_FILENAME'] ?? '')) {
    $bridge = new PiemApiBridge();
    $acao = $_GET['action'] ?? 'tutor';

    if ($acao === 'tutor') {
        $pergunta = $_GET['q'] ?? 'Como posso começar meu projeto de tecnologia?';
        echo json_encode($bridge->askTutor($pergunta), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    } else {
        echo json_encode(array(
            'sistema' => 'PIEM Tusker Power PHP Bridge',
            'versao' => '3.0.0',
            'status' => 'ativo',
            'modos_suportados' => array('tutor', 'supabase_projects')
        ), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    }
}
