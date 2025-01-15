declare module 'plotly.js-dist' {
  export interface PlotData {
    type: string;
    x?: (string | number)[];
    y?: (string | number)[];
    z?: (number | number[])[];
    text?: string | string[] | string[][];
    mode?: string;
    name?: string;
    colorscale?: Array<[number, string]>;
    showscale?: boolean;
    hoverongaps?: boolean;
    texttemplate?: string;
    textfont?: {
      size?: number;
      color?: string;
    };
    marker?: {
      color?: string;
      line?: {
        color?: string;
        width?: number;
      };
    };
    line?: {
      color?: string;
      width?: number;
    };
    fill?: string;
    fillcolor?: string;
    hovertemplate?: string;
    hoverlabel?: {
      bgcolor?: string;
      font?: {
        color?: string;
      };
    };
    node?: {
      pad?: number;
      thickness?: number;
      line?: {
        color?: string;
        width?: number;
      };
      label?: string[];
      color?: string[];
      hoverongaps?: boolean;
      hoverlabel?: {
        bgcolor?: string;
        font?: {
          color?: string;
        };
      };
    };
    link?: {
      source?: number[];
      target?: number[];
      value?: number[];
      color?: string[];
      hovertemplate?: string;
    };
    r?: number[];
    theta?: string[];
    orientation?: 'h' | 'v';
    nbinsx?: number;
  }

  export interface Layout {
    title?: string | {
      text?: string;
      font?: {
        size?: number;
        color?: string;
      };
    };
    height?: number;
    width?: number;
    margin?: {
      t?: number;
      b?: number;
      l?: number;
      r?: number;
    };
    xaxis?: {
      title?: string;
      tickangle?: number;
      tickfont?: {
        size?: number;
      };
      tickformat?: string;
      range?: number[];
    };
    yaxis?: {
      title?: string;
      tickformat?: string;
    };
    paper_bgcolor?: string;
    plot_bgcolor?: string;
    font?: {
      color?: string;
    };
    polar?: {
      radialaxis?: {
        visible?: boolean;
        range?: number[];
        tickformat?: string;
      };
    };
    showlegend?: boolean;
    bargap?: number;
  }

  export interface Config {
    responsive?: boolean;
    displayModeBar?: boolean;
  }

  export function newPlot(
    graphDiv: HTMLElement | null,
    data: Partial<PlotData>[],
    layout?: Partial<Layout>,
    config?: Partial<Config>
  ): Promise<void>;

  export function purge(graphDiv: HTMLElement | null): void;
}

declare module 'plotly.js-dist-min' {
  export * from 'plotly.js-dist';
} 