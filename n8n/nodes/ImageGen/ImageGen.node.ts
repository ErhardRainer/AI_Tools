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
 * ImageGen Node — generiert Bilder aus Text-Prompts via Media API.
 *
 * Unterstützte Provider (über llm-api Service):
 *   openai, google, stability, fal, ideogram, leonardo, firefly,
 *   auto1111 (lokal), ollamadiffuser (lokal)
 *
 * Rückgabe: provider, model, images[] (mit url und/oder b64_json je Provider),
 *           optional revised_prompt (DALL-E 3)
 *
 * Voraussetzung: Media API (llm-api Service) muss laufen.
 *   cd llm-api && uvicorn api:app --reload
 */
export class ImageGenNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Image Generator',
    name: 'imageGen',
    icon: 'fa:image',
    iconColor: 'blue',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["provider"] || $parameter["preset"]}}',
    description: 'Generiert Bilder aus Text-Prompts via Media API (DALL-E, Imagen, FLUX, Ideogram, …)',
    defaults: {
      name: 'Image Generator',
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
        description: 'Bildgenerierungs-Provider. Wird von Preset überschrieben falls angegeben.',
        options: [
          { name: 'OpenAI (DALL-E)',                 value: 'openai' },
          { name: 'Google (Imagen 4 / Gemini Flash)', value: 'google' },
          { name: 'Stability AI (SD3.5 / Core)',     value: 'stability' },
          { name: 'fal.ai (FLUX)',                   value: 'fal' },
          { name: 'Ideogram (V3)',                   value: 'ideogram' },
          { name: 'Leonardo AI',                     value: 'leonardo' },
          { name: 'Adobe Firefly',                   value: 'firefly' },
          { name: 'AUTOMATIC1111 (lokal)',            value: 'auto1111' },
          { name: 'ollamadiffuser (lokal)',           value: 'ollamadiffuser' },
        ],
      },
      {
        displayName: 'Preset',
        name: 'preset',
        type: 'string',
        default: '',
        placeholder: 'flux, sd3.5, imagen4, ideogram, local-flux, …',
        description:
          'Optionaler Preset-Alias aus der ImageGen/config.json. ' +
          'Überschreibt Provider und Modell.',
      },
      {
        displayName: 'Modell',
        name: 'model',
        type: 'string',
        default: '',
        placeholder: 'dall-e-3, imagen-4.0-generate-001, V_3, flux.1-schnell, …',
        description: 'Modell überschreiben (optional). Leer = Provider-Standard.',
      },

      // ── Prompt ────────────────────────────────────────────────────────────
      {
        displayName: 'Prompt',
        name: 'prompt',
        type: 'string',
        typeOptions: { rows: 4 },
        default: '',
        description: 'Beschreibung des zu generierenden Bildes.',
        required: true,
      },

      // ── Anzahl Bilder ─────────────────────────────────────────────────────
      {
        displayName: 'Anzahl Bilder',
        name: 'n',
        type: 'number',
        typeOptions: { minValue: 1, maxValue: 10 },
        default: 1,
        description: 'Anzahl der zu generierenden Bilder (1–10).',
      },

      // ── Provider-spezifische Optionen ─────────────────────────────────────
      {
        displayName: 'Seitenverhältnis',
        name: 'aspectRatio',
        type: 'options',
        default: '1:1',
        description:
          'Seitenverhältnis (Stability AI, Google Imagen, Ideogram, fal.ai). ' +
          'Wird ignoriert bei DALL-E, Firefly, A1111.',
        options: [
          { name: 'Quadrat (1:1)',     value: '1:1' },
          { name: 'Querformat (16:9)', value: '16:9' },
          { name: 'Hochformat (9:16)', value: '9:16' },
          { name: 'Querformat (4:3)',  value: '4:3' },
          { name: 'Hochformat (3:4)',  value: '3:4' },
          { name: 'Ultra-Quer (21:9)', value: '21:9' },
        ],
      },
      {
        displayName: 'Bildgröße (WxH)',
        name: 'size',
        type: 'options',
        default: '1024x1024',
        description:
          'Bildgröße in Pixeln (DALL-E 3, Firefly, AUTOMATIC1111). ' +
          'Wird ignoriert bei Stability AI, Google Imagen, Ideogram, fal.ai.',
        options: [
          { name: '1024×1024 (Quadrat)',   value: '1024x1024' },
          { name: '1792×1024 (Querformat)', value: '1792x1024' },
          { name: '1024×1792 (Hochformat)', value: '1024x1792' },
          { name: '2048×1152 (Firefly Wide)', value: '2048x1152' },
          { name: '512×512 (A1111 Standard)', value: '512x512' },
        ],
      },
      {
        displayName: 'Qualität',
        name: 'quality',
        type: 'options',
        default: 'standard',
        description: 'Bildqualität (nur DALL-E 3).',
        options: [
          { name: 'Standard', value: 'standard' },
          { name: 'HD',       value: 'hd' },
        ],
        displayOptions: {
          show: {
            provider: ['openai'],
          },
        },
      },

      // ── Ausgabe ───────────────────────────────────────────────────────────
      {
        displayName: 'Bild-Ausgabe',
        name: 'imageOutput',
        type: 'options',
        default: 'both',
        description: 'Welche Bild-Daten weitergegeben werden.',
        options: [
          {
            name: 'URL und Base64',
            value: 'both',
            description: 'Alle verfügbaren Bild-Daten (URL und/oder b64_json)',
          },
          {
            name: 'Nur URL',
            value: 'url',
            description: 'Nur Bild-URL (falls Provider eine URL zurückgibt)',
          },
          {
            name: 'Nur Base64',
            value: 'b64',
            description: 'Nur base64-kodiertes Bild (für direkte Weiterverarbeitung)',
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
        const prompt      = this.getNodeParameter('prompt',      i) as string;
        const n           = this.getNodeParameter('n',           i) as number;
        const aspectRatio = this.getNodeParameter('aspectRatio', i) as string;
        const size        = this.getNodeParameter('size',        i) as string;
        const quality     = this.getNodeParameter('quality',     i) as string;
        const imageOutput = this.getNodeParameter('imageOutput', i) as string;

        const body: Record<string, string | number> = { prompt, n };

        if (preset) {
          body.preset = preset;
        } else {
          body.provider = provider;
        }
        if (model)       body.model        = model;
        if (aspectRatio) body.aspect_ratio = aspectRatio;
        if (size)        body.size         = size;
        if (quality)     body.quality      = quality;

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };
        if (apiKey) headers['X-API-Key'] = apiKey;

        const options: IHttpRequestOptions = {
          method: 'POST',
          url: `${baseUrl}/image`,
          headers,
          body,
          json: true,
        };

        const response = await this.helpers.httpRequest(options);

        // Bilder je nach Ausgabe-Einstellung filtern
        const images = (response.images as Array<{ url?: string; b64_json?: string }>).map(
          (img) => {
            if (imageOutput === 'url')  return { url: img.url };
            if (imageOutput === 'b64') return { b64_json: img.b64_json };
            return img; // 'both'
          },
        );

        returnData.push({
          json: {
            provider:       response.provider,
            model:          response.model,
            revised_prompt: response.revised_prompt ?? null,
            images,
            image_count:    images.length,
            // Erster Bild-URL für einfache Weiterverwendung
            first_url:    images[0]?.url    ?? null,
            first_b64:    images[0]?.b64_json ?? null,
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
