import {
  IAuthenticateGeneric,
  ICredentialTestRequest,
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

/**
 * Credentials für die Media API (llm-api FastAPI-Service).
 *
 * Die Media API ist der lokale FastAPI-Wrapper aus dem llm-api/ Verzeichnis.
 * Standard-URL: http://localhost:8000
 *
 * API_KEY ist optional — nur setzen wenn der Service mit API_KEY Env-Variable gestartet wurde.
 */
export class MediaApiCredentials implements ICredentialType {
  name = 'mediaApiCredentials';
  displayName = 'Media API (llm-api Service)';
  documentationUrl = 'https://github.com/ErhardRainer/OpenAI/tree/master/llm-api';

  properties: INodeProperties[] = [
    {
      displayName: 'Base URL',
      name: 'baseUrl',
      type: 'string',
      default: 'http://localhost:8000',
      placeholder: 'http://localhost:8000',
      description:
        'URL des laufenden llm-api FastAPI-Service. ' +
        'Starten mit: cd llm-api && uvicorn api:app --reload',
    },
    {
      displayName: 'API Key (optional)',
      name: 'apiKey',
      type: 'string',
      typeOptions: { password: true },
      default: '',
      description:
        'Optionaler API-Key (Header: X-API-Key). ' +
        'Nur setzen wenn der Service mit der Env-Variable API_KEY gestartet wurde.',
    },
  ];

  // Setzt X-API-Key Header wenn ein Key konfiguriert ist
  authenticate: IAuthenticateGeneric = {
    type: 'generic',
    properties: {
      headers: {
        'X-API-Key': '={{$credentials.apiKey}}',
      },
    },
  };

  // Credential-Test: GET /health prüfen
  test: ICredentialTestRequest = {
    request: {
      baseURL: '={{$credentials.baseUrl}}',
      url: '/health',
      method: 'GET',
    },
  };
}
