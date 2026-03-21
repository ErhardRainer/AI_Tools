import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  IHttpRequestOptions,
  NodeConnectionTypes,
  NodeOperationError,
} from 'n8n-workflow';

/**
 * LLM Client Node — sendet Text-Prompts an einen LLM-Provider via Media API.
 *
 * Unterstützte Provider (über llm-api Service):
 *   openai, claude, gemini, grok, kimi, deepseek, groq, mistral
 *
 * Der Node sendet System-, Kontext- und Aufgaben-Prompt (drei-stufige Prompt-Architektur)
 * und gibt die Modellantwort als Text oder extrahiertes JSON zurück.
 *
 * Voraussetzung: Media API (llm-api Service) muss laufen.
 *   cd llm-api && uvicorn api:app --reload
 */
export class LlmClientNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'LLM Client',
    name: 'llmClient',
    icon: 'fa:comments',
    iconColor: 'crimson',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["provider"] || $parameter["preset"]}}',
    description: 'Sendet Text-Prompts an LLM-Provider via Media API (OpenAI, Claude, Gemini, Grok, …)',
    defaults: {
      name: 'LLM Client',
    },
    inputs: [NodeConnectionTypes.Main],
    outputs: [NodeConnectionTypes.Main],
    credentials: [
      {
        name: 'mediaApiCredentials',
        required: true,
      },
    ],
    properties: [
      // ── Provider ──────────────────────────────────────────────────────────
      {
        displayName: 'Provider',
        name: 'provider',
        type: 'options',
        default: 'openai',
        description: 'LLM-Provider. Wird von Preset überschrieben falls angegeben.',
        options: [
          { name: 'OpenAI (GPT)',       value: 'openai' },
          { name: 'Claude (Anthropic)', value: 'claude' },
          { name: 'Gemini (Google)',    value: 'gemini' },
          { name: 'Grok (xAI)',         value: 'grok' },
          { name: 'Kimi (Moonshot)',    value: 'kimi' },
          { name: 'DeepSeek',           value: 'deepseek' },
          { name: 'Groq',               value: 'groq' },
          { name: 'Mistral',            value: 'mistral' },
        ],
      },
      {
        displayName: 'Preset',
        name: 'preset',
        type: 'string',
        default: '',
        placeholder: 'coding, fast, translate, …',
        description:
          'Optionaler Preset-Alias aus der LLM_Client/config.json. ' +
          'Überschreibt Provider und Modell.',
      },
      {
        displayName: 'Modell',
        name: 'model',
        type: 'string',
        default: '',
        placeholder: 'gpt-4o, claude-sonnet-4-6, gemini-2.0-flash, …',
        description: 'Modell überschreiben (optional). Leer = Provider-Standard.',
      },

      // ── Prompts ───────────────────────────────────────────────────────────
      {
        displayName: 'System-Prompt',
        name: 'system',
        type: 'string',
        typeOptions: { rows: 3 },
        default: 'You are a helpful assistant.',
        description: 'Rollenanweisung / System-Prompt für das Modell.',
        required: true,
      },
      {
        displayName: 'Kontext',
        name: 'context',
        type: 'string',
        typeOptions: { rows: 5 },
        default: '',
        description:
          'Optionaler Hintergrundtext: Dokument, E-Mail, Code, URL, … ' +
          'HTTP(S)-URLs werden automatisch abgerufen und durch den Inhalt ersetzt. ' +
          'Leer lassen wenn nicht benötigt.',
      },
      {
        displayName: 'Aufgabe / Nachricht',
        name: 'task',
        type: 'string',
        typeOptions: { rows: 4 },
        default: '',
        description: 'Die eigentliche Aufgabe, Frage oder Nutzernachricht.',
        required: true,
      },

      // ── Ausgabe ───────────────────────────────────────────────────────────
      {
        displayName: 'Ausgabeformat',
        name: 'outputFormat',
        type: 'options',
        default: 'plain',
        options: [
          {
            name: 'Plain Text',
            value: 'plain',
            description: 'Rohe Modellantwort als Text',
          },
          {
            name: 'JSON (extrahiert)',
            value: 'json',
            description:
              'Extrahiert den ersten JSON-Block aus der Antwort. ' +
              'Fehler wenn kein gültiges JSON vorhanden.',
          },
        ],
      },
    ],
  };

  // ── Ausführung ─────────────────────────────────────────────────────────────

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];
    const credentials = await this.getCredentials('mediaApiCredentials');

    const baseUrl = (credentials.baseUrl as string).replace(/\/$/, '');
    const apiKey  = credentials.apiKey as string;

    for (let i = 0; i < items.length; i++) {
      try {
        const provider    = this.getNodeParameter('provider',    i) as string;
        const preset      = this.getNodeParameter('preset',      i) as string;
        const model       = this.getNodeParameter('model',       i) as string;
        const system      = this.getNodeParameter('system',      i) as string;
        const context     = this.getNodeParameter('context',     i) as string;
        const task        = this.getNodeParameter('task',        i) as string;
        const outputFormat = this.getNodeParameter('outputFormat', i) as string;

        const body: Record<string, string> = { system, context, task };

        // Preset hat Vorrang — wenn gesetzt, keinen provider/model mitschicken
        if (preset) {
          body.preset = preset;
        } else {
          body.provider = provider;
        }
        if (model) body.model = model;
        if (outputFormat !== 'plain') body.output_format = outputFormat;

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };
        if (apiKey) headers['X-API-Key'] = apiKey;

        const options: IHttpRequestOptions = {
          method: 'POST',
          url: `${baseUrl}/chat`,
          headers,
          body,
          json: true,
        };

        const response = await this.helpers.httpRequest(options);

        returnData.push({
          json: {
            provider:  response.provider,
            model:     response.model,
            response:  response.response,
            // Vollständige Antwort für Weitergabe
            _raw: response,
          },
          pairedItem: { item: i },
        });

      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: { error: (error as Error).message },
            pairedItem: { item: i },
          });
          continue;
        }
        throw new NodeOperationError(this.getNode(), error as Error, {
          itemIndex: i,
        });
      }
    }

    return [returnData];
  }
}
