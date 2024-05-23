import unittest
import os
import json
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, mock_open

class TestGetDocumentosEndpoint(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)

    def test_get_documentos_endpoint(self):
        # Datos de ejemplo para enviar en el cuerpo de la solicitud
        body_data = {
            "id": "10"  # Cambia este valor por el ID correcto
        }

        # Simular una solicitud POST al endpoint /universidades/
        response = self.client.post("/universidades/", json=body_data)

        # Verificar que la respuesta tenga un código de estado 200
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta contiene documentos
        self.assertTrue(response.json())

client = TestClient(app)


def test_query_title_endpoint():
    # Define el título de ejemplo para buscar en los documentos
    title_to_search = "The University of Chicago: Graduate Studies"

    # Mock para glob.glob que simula la lista de archivos JSON
    with patch("glob.glob") as mock_glob:
        mock_glob.return_value = ["archivos_json/university_1.json", "archivos_json/university_2.json"]

        # Mock para open que simula la carga de datos desde los archivos JSON
        with patch("builtins.open", mock_open(read_data='[{"title": "The University of Chicago: Graduate Studies", "content": "Contenido 1"}]')):

            # Mock para json.load que simula la carga de datos JSON desde los archivos
            with patch("json.load") as mock_load:
                mock_load.side_effect = [
                    [
                        {"title": "The University of Chicago: Graduate Studies", "content": "Contenido 1"},
                        {"title": "Título 2", "content": "Contenido 2"}
                    ],
                    [
                        {"title": "Título 3", "content": "Contenido 3"},
                        {"title": "Ejemplo de título", "content": "Contenido 4"}
                    ]
                ]

                # Realiza una solicitud POST al endpoint /universidades/consulta-titulo/
                response = client.post("/universidades/consulta-titulo/", params={"title": title_to_search})

    # Verifica que la respuesta tenga un código de estado 200
    assert response.status_code == 200

    # Verifica que la respuesta contiene los resultados esperados
    expected_results = [
        {"title": "The University of Chicago: Graduate Studies", "content": "Contenido 1"}
    ]
    assert response.json() == expected_results

def test_list_universidades():
    # Mock para os.listdir que simula la lista de carpetas en "dataset"
    with patch("os.listdir") as mock_listdir:
        mock_listdir.return_value = ["university1_folder", "university2_folder"]

        # Mock para get_university_name que simula la obtención del nombre de la universidad
        with patch("main.get_university_name") as mock_get_university_name:
            mock_get_university_name.side_effect = ["University 1", "University 2"]

            # Realiza una solicitud GET al endpoint /universidades/list
            response = client.get("/universidades/list")

    # Verifica que la respuesta tenga un código de estado 200
    assert response.status_code == 200

    # Verifica que la respuesta contiene las universidades esperadas
    expected_response = [
        {"id": "1_folder", "name": "University 1"},
        {"id": "2_folder", "name": "University 2"}
    ]
    assert response.json() == expected_response

class TestSendDatosEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_enviar_datos_endpoint(self):
        response = self.client.post("/enviar-datos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Datos scrapeados enviados correctamente al microservicio"})

if __name__ == "__main__":
    unittest.main()