import {
  Callout,
  Grid,
  H1,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
} from "cursor/canvas";

type View = "both" | "fit" | "test";
type Slice = "all" | "executed" | "generative" | "retrieval" | "unrun";
type Family =
  | "nano30"
  | "nano4"
  | "lightning"
  | "super"
  | "ultra"
  | "omni"
  | "embed"
  | "tools";
type Tone = "success" | "danger" | "warning" | "info" | "neutral";
type Fit = "1×" | "1× tight" | "2×" | "4× tight" | "8×" | "doesn't fit" | "n/a";

type Cell = {
  test: string;
  fit: Fit;
  why?: string;
};

type MatrixRow = {
  model: string;
  precision: string;
  weights: string;
  family: Family;
  tone: Tone;
  executed: boolean;
  mi300x: Cell;
  mi325x: Cell;
  mi350x: Cell;
  mi355x: Cell;
  mi350p: Cell;
  radeon: Cell;
  ryzen: Cell;
};

const NYV: Cell = { test: "NYV", fit: "1×" };
const NYV_TIGHT: Cell = { test: "NYV", fit: "1× tight" };
const NYV_FNUZ: Cell = {
  test: "NYV",
  fit: "1×",
  why: "NVIDIA FP8 and MI300/MI325 FP8 (FNUZ) are different formats",
};
const NYV_NV: Cell = { test: "NYV", fit: "1×" };
const NYV_NV_MI350: Cell = { test: "NYV", fit: "1×" };
const NT_1X: Cell = { test: "NT", fit: "1×" };
const NT_NV: Cell = { test: "NT", fit: "1×" };
const PCIE_NO: Cell = {
  test: "NP",
  fit: "doesn't fit",
  why: "Fit counts one PCIe card only",
};
const LAPTOP_NO: Cell = {
  test: "NP",
  fit: "doesn't fit",
  why: "Too large for a Ryzen AI laptop (93 GB RAM, 512 MB dedicated iGPU)",
};
const RADEON_SMALL: Cell = {
  test: "NT",
  fit: "1×",
  why: "Would likely fit a 16 GB or larger Radeon",
};
const RYZEN_SMALL: Cell = {
  test: "NT",
  fit: "1×",
  why: "Would fit Ryzen AI laptop CPU memory; iGPU and NPU untested",
};

const ROWS: MatrixRow[] = [
  {
    model: "Nano 30B-A3B",
    precision: "BF16",
    weights: "~56 GiB",
    family: "nano30",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val + Runs",
      fit: "1×",
      why: "Transformers smoke passed; vLLM also served through 128K context",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Nano 30B-A3B",
    precision: "FP8",
    weights: "~28 GiB",
    family: "nano30",
    tone: "danger",
    executed: true,
    mi300x: {
      test: "FAIL",
      fit: "1×",
      why: "Failed importing mamba-ssm; NVIDIA FP8 may not match MI300X FP8 (FNUZ)",
    },
    mi325x: NYV_FNUZ,
    mi350x: {
      test: "NYV",
      fit: "1×",
      why: "MI350-series FP8 is closer to NVIDIA’s, but still untested",
    },
    mi355x: NYV,
    mi350p: NYV,
    radeon: {
      test: "NT",
      fit: "1× tight",
      why: "Fits larger Radeons only; 16–24 GB cards are too small",
    },
    ryzen: {
      test: "NT",
      fit: "1×",
      why: "CPU RAM would hold ~28 GiB. Dedicated iGPU 512 MB doesn't fit. NPU untested.",
    },
  },
  {
    model: "Nano 30B-A3B",
    precision: "NVFP4",
    weights: "~15–21 GiB",
    family: "nano30",
    tone: "info",
    executed: false,
    mi300x: NT_NV,
    mi325x: NYV_NV,
    mi350x: NYV_NV_MI350,
    mi355x: NYV_NV_MI350,
    mi350p: NYV_NV_MI350,
    radeon: {
      test: "NT",
      fit: "1×",
    },
    ryzen: { test: "NA", fit: "n/a" },
  },
  {
    model: "Nano 30B-A3B",
    precision: "GGUF Q4_K_M (Unsloth)",
    weights: "22.88 GiB",
    family: "nano30",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val",
      fit: "1×",
      why: "llama.cpp HIP gfx942, 53/53 layers on ROCm0, ~23197 MiB buffer (231304Z). Community unsloth/ file, not official NVIDIA 30B GGUF",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×", why: "HIP/Vulkan support on discrete Radeon is unknown" },
    ryzen: {
      test: "Val CPU + Val iGPU",
      fit: "1×",
      why: "CPU llama.cpp b10453 225528Z. Vulkan RADV GFX1150 UMA ~47 GiB, 53/53 layers, ~23197 MiB buffer 225631Z. Ryzen AI dedicated iGPU 512 MB does not fit. NPU untested. Not official NVIDIA 30B GGUF",
    },
  },
  {
    model: "Nano 4B",
    precision: "BF16",
    weights: "~7.4 GiB",
    family: "nano4",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val + Runs",
      fit: "1×",
      why: "Transformers Validated. vLLM also served at 8192 context (170637Z)",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Nano 4B",
    precision: "FP8",
    weights: "~4 GB class",
    family: "nano4",
    tone: "warning",
    executed: true,
    mi300x: {
      test: "Runs",
      fit: "1×",
      why: "Loaded and generated looping A tokens; likely FP8 FNUZ mismatch. Not Validated (170427Z)",
    },
    mi325x: NYV_FNUZ,
    mi350x: { test: "NYV", fit: "1×", why: "MI350-series FP8 is closer to NVIDIA’s, but still untested" },
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Nano 4B",
    precision: "GGUF Q4_K_M",
    weights: "2.64 GiB",
    family: "nano4",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val",
      fit: "1×",
      why: "llama.cpp HIP gfx942, 43/43 layers on ROCm0 (215228Z)",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×" },
    ryzen: {
      test: "Val CPU + Val iGPU",
      fit: "1×",
      why: "CPU llama.cpp b10453 214142Z. Vulkan RADV GFX1150 UMA ~47 GiB, 43/43 layers 214348Z. Ryzen AI NPU untested",
    },
  },
  {
    model: "Lightning 30B-A3B",
    precision: "BF16",
    weights: "~56 GiB",
    family: "lightning",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val + Runs",
      fit: "1×",
      why: "Transformers Validated. vLLM also served at 8192 context (170852Z). Not Nano 30B",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Lightning 30B-A3B",
    precision: "GGUF Q4_0 (ggml-org)",
    weights: "17.60 GiB",
    family: "lightning",
    tone: "success",
    executed: true,
    mi300x: {
      test: "Val",
      fit: "1×",
      why: "llama.cpp HIP gfx942, 53/53 layers on ROCm0, ~17658 MiB buffer (225542Z)",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×" },
    ryzen: {
      test: "Val CPU + Val iGPU",
      fit: "1×",
      why: "CPU llama.cpp b10453 223932Z. Vulkan RADV GFX1150 UMA, 53/53 layers 224120Z. Ryzen AI dedicated iGPU 512 MB does not fit. NPU untested",
    },
  },
  {
    model: "Lightning 30B-A3B",
    precision: "FP8",
    weights: "—",
    family: "lightning",
    tone: "neutral",
    executed: false,
    mi300x: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    mi325x: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    mi350x: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    mi355x: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    mi350p: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    radeon: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
    ryzen: { test: "Skip", fit: "n/a", why: "NVIDIA published no official Hugging Face download" },
  },
  {
    model: "Lightning 30B-A3B",
    precision: "NVFP4",
    weights: "~15 GB class",
    family: "lightning",
    tone: "info",
    executed: false,
    mi300x: NT_NV,
    mi325x: NYV_NV,
    mi350x: NYV_NV_MI350,
    mi355x: NYV_NV_MI350,
    mi350p: NYV_NV_MI350,
    radeon: { test: "NT", fit: "1×" },
    ryzen: { test: "NT", fit: "n/a" },
  },
  {
    model: "Super 120B-A12B",
    precision: "BF16",
    weights: "~224 GiB",
    family: "super",
    tone: "info",
    executed: false,
    mi300x: { test: "NT", fit: "2×", why: "Would need 2 GPUs; not downloaded" },
    mi325x: NYV_TIGHT,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: PCIE_NO,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Super 120B-A12B",
    precision: "FP8",
    weights: "~112 GiB",
    family: "super",
    tone: "danger",
    executed: true,
    mi300x: { test: "FAIL", fit: "1×", why: "Failed importing mamba-ssm; NVIDIA FP8 may not match MI300X FP8 (FNUZ)" },
    mi325x: NYV_FNUZ,
    mi350x: { test: "NYV", fit: "1×", why: "MI350-series FP8 is closer to NVIDIA’s, but still untested" },
    mi355x: NYV,
    mi350p: NYV_TIGHT,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Super 120B-A12B",
    precision: "NVFP4",
    weights: "~60 GB payload",
    family: "super",
    tone: "info",
    executed: false,
    mi300x: NT_NV,
    mi325x: NYV_NV,
    mi350x: NYV_NV_MI350,
    mi355x: NYV_NV_MI350,
    mi350p: NYV_NV_MI350,
    radeon: { test: "NP", fit: "doesn't fit", why: "About 60 GB of weights vs at most 48 GB on a Radeon" },
    ryzen: LAPTOP_NO,
  },
  {
    model: "Ultra 550B-A55B",
    precision: "BF16",
    weights: "~1.1 TB",
    family: "ultra",
    tone: "info",
    executed: false,
    mi300x: { test: "NT", fit: "8×", why: "Four of these GPUs together still cannot hold about 1100 GB of weights" },
    mi325x: { test: "NT", fit: "8×", why: "Four of these 256 GB GPUs still cannot hold about 1100 GB of weights" },
    mi350x: { test: "NYV", fit: "4× tight", why: "About 13 GB of memory left per GPU after the weights — little room for context" },
    mi355x: { test: "NYV", fit: "4× tight", why: "About 13 GB of memory left per GPU after the weights — little room for context" },
    mi350p: PCIE_NO,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Ultra 550B-A55B",
    precision: "NVFP4",
    weights: "~275 GB payload",
    family: "ultra",
    tone: "info",
    executed: false,
    mi300x: { test: "NT", fit: "2×" },
    mi325x: { test: "NT", fit: "2×" },
    mi350x: { test: "NYV", fit: "1× tight", why: "About 13 GB leftover after the weights" },
    mi355x: { test: "NYV", fit: "1× tight", why: "About 13 GB leftover after the weights" },
    mi350p: { test: "NP", fit: "doesn't fit" },
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Nano Omni 30B",
    precision: "BF16",
    weights: "62 GB listed",
    family: "omni",
    tone: "danger",
    executed: true,
    mi300x: { test: "FAIL", fit: "1×", why: "Vision encoder rejected the dummy image size after other load workarounds" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: PCIE_NO,
    ryzen: LAPTOP_NO,
  },
  {
    model: "Nano Omni 30B",
    precision: "FP8",
    weights: "33 GB listed",
    family: "omni",
    tone: "danger",
    executed: true,
    mi300x: { test: "FAIL", fit: "1×", why: "Failed importing mamba-ssm; NVIDIA FP8 may not match MI300X FP8 (FNUZ)" },
    mi325x: NYV_FNUZ,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: {
      test: "NT",
      fit: "1× tight",
      why: "Fits larger Radeons only; 16–24 GB cards are too small",
    },
    ryzen: {
      test: "NT",
      fit: "1×",
      why: "CPU RAM would hold ~33 GB listed. Dedicated iGPU 512 MB doesn't fit. NPU untested.",
    },
  },
  {
    model: "Nano Omni 30B",
    precision: "NVFP4",
    weights: "21 GB listed",
    family: "omni",
    tone: "info",
    executed: false,
    mi300x: NT_NV,
    mi325x: NYV_NV,
    mi350x: NYV_NV_MI350,
    mi355x: NYV_NV_MI350,
    mi350p: NYV_NV_MI350,
    radeon: { test: "NT", fit: "1×" },
    ryzen: { test: "NT", fit: "n/a" },
  },
  {
    model: "Embed 1B",
    precision: "BF16",
    weights: "~2.3 GB",
    family: "embed",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Embedding similarity worked; not a retrieval benchmark" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Embed 1B",
    precision: "NVFP4",
    weights: "~0.5 GiB",
    family: "embed",
    tone: "info",
    executed: false,
    mi300x: NT_NV,
    mi325x: NYV_NV,
    mi350x: NYV_NV_MI350,
    mi355x: NYV_NV_MI350,
    mi350p: NYV_NV_MI350,
    radeon: { test: "NA", fit: "n/a" },
    ryzen: { test: "NA", fit: "n/a" },
  },
  {
    model: "Embed 8B",
    precision: "BF16",
    weights: "~16 GB",
    family: "embed",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Embedding similarity worked, with a Yarn scaling warning" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×", why: "Would likely need a 24 GB or larger Radeon" },
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Rerank 1B v2",
    precision: "BF16",
    weights: "~2 GB class",
    family: "embed",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Relevant text scored higher than irrelevant text" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "VL embed 1B v2",
    precision: "BF16",
    weights: "~2 GB class",
    family: "embed",
    tone: "warning",
    executed: true,
    mi300x: {
      test: "Runs",
      fit: "1×",
      why: "Model loaded on a dummy image, but returned an empty embedding",
    },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "VL embed 1B v2",
    precision: "FP8",
    weights: "~1 GB class",
    family: "embed",
    tone: "danger",
    executed: true,
    mi300x: {
      test: "FAIL",
      fit: "1×",
      why: "create_bidirectional_mask missing inputs_embeds (170519Z). R-FNUZ",
    },
    mi325x: NYV_FNUZ,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "VL rerank 1B v2",
    precision: "BF16",
    weights: "~2 GB class",
    family: "embed",
    tone: "warning",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Text ranking worked; images were not ranked" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "VL rerank 1B v2",
    precision: "FP8",
    weights: "~1 GB class",
    family: "embed",
    tone: "danger",
    executed: true,
    mi300x: {
      test: "FAIL",
      fit: "1×",
      why: "Loaded, but relevant scored worse than irrelevant (170557Z). R-FNUZ",
    },
    mi325x: NYV_FNUZ,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "ColEmbed VL 3B/4B/8B",
    precision: "BF16",
    weights: "~6–16 GB",
    family: "embed",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Produced an embedding from a dummy image on all three sizes" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×", why: "The 8B size needs about 24 GB; smaller Radeons are too small" },
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Omni embed 3B",
    precision: "BF16",
    weights: "~6 GB class",
    family: "embed",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Embedded a dummy image; not the Omni 30B language model" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Parse 2.0",
    precision: "BF16",
    weights: "listed ~VISION",
    family: "tools",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Generated text from a dummy image; not an OCR accuracy test" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "ASR 3.5 0.6B",
    precision: "default",
    weights: "~0.6B",
    family: "tools",
    tone: "warning",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Speech pipeline loaded; a synthetic tone produced empty transcript" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Content Safety 3.5",
    precision: "BF16",
    weights: "~8 GB class",
    family: "tools",
    tone: "success",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Returned a safety label on a harmless prompt; not a red-team" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: RADEON_SMALL,
    ryzen: RYZEN_SMALL,
  },
  {
    model: "Safety Guard 8B v3",
    precision: "BF16",
    weights: "~16 GB",
    family: "tools",
    tone: "warning",
    executed: true,
    mi300x: { test: "Runs", fit: "1×", why: "Generated text, but answered like a chatbot instead of a safety filter" },
    mi325x: NYV,
    mi350x: NYV,
    mi355x: NYV,
    mi350p: NYV,
    radeon: { test: "NT", fit: "1×", why: "Would likely need a 24 GB or larger Radeon" },
    ryzen: RYZEN_SMALL,
  },
];

const PLATFORM_KEYS = [
  "mi300x",
  "mi325x",
  "mi350x",
  "mi355x",
  "mi350p",
  "radeon",
  "ryzen",
] as const;

type PlatformKey = (typeof PLATFORM_KEYS)[number];

const OAM_KEYS = new Set<PlatformKey>([
  "mi300x",
  "mi325x",
  "mi350x",
  "mi355x",
]);

const PLATFORM_HEADERS = [
  "MI300X OAM (executed)",
  "MI325X OAM (not executed)",
  "MI350X OAM (not executed)",
  "MI355X OAM (not executed)",
  "MI350P PCIe (not executed)",
  "Discrete Radeon (not executed)",
  "Ryzen AI laptop",
];

function verdict(cell: Cell): string {
  if (cell.fit === "doesn't fit") return "DOESN'T FIT";
  switch (cell.test) {
    case "Val":
    case "Val + Runs":
    case "Val CPU + Val iGPU":
      return "VALIDATED";
    case "Runs":
      return "RAN — not validated";
    case "FAIL":
      return "FAILED";
    case "NP":
      return "DOESN'T FIT";
    case "NA":
      return "NO SOFTWARE PATH";
    case "Skip":
      return "NO OFFICIAL FILE";
    default:
      return "NOT TESTED";
  }
}

function detailLine(cell: Cell): string | undefined {
  if (cell.fit === "doesn't fit") {
    return "Weights exceed that one PCIe GPU or a Ryzen AI laptop. That is not a not-tested result.";
  }
  switch (cell.test) {
    case "Val + Runs":
      return "Answers looked right in Transformers. Also served in vLLM — that serving path is not a validation.";
    case "Val CPU + Val iGPU":
      return "llama.cpp on the Ryzen AI laptop CPU and iGPU (Vulkan). Not the NPU.";
    case "Val":
      return "A recorded smoke test ran; the answers looked right.";
    case "Runs":
      return "Loaded and produced output. That is not the same as validated, fast, or production-ready.";
    case "FAIL":
      return "Execution on MI300X did not generate usable output.";
    case "Skip":
      return "NVIDIA did not publish an official download for this precision.";
    case "NA":
      return "No Nemotron software path identified on that target.";
    case "NP":
      return "Weights exceed that one PCIe GPU or a Ryzen AI laptop.";
    default:
      return "Not executed. Weights would fit; fitting in memory is still not a pass.";
  }
}

function memoryLabel(
  fit: Fit,
  hypothetical: boolean,
  key: PlatformKey,
): string {
  const oam = OAM_KEYS.has(key);
  switch (fit) {
    case "1×":
      if (oam) {
        return hypothetical
          ? "Would fit 1 OAM GPU"
          : "Fits 1 OAM GPU";
      }
      return hypothetical ? "Would fit 1 GPU" : "Fits 1 GPU";
    case "1× tight":
      if (oam) {
        return hypothetical
          ? "Would fit 1 OAM GPU, little leftover for context"
          : "Fits 1 OAM GPU, little leftover for context";
      }
      return hypothetical
        ? "Would fit 1 GPU, little leftover for context"
        : "Fits 1 GPU, little leftover for context";
    case "2×":
      return "Would need 2 OAM GPUs on a UBB-class node";
    case "4× tight":
      return "Would need 4 OAM GPUs, little leftover";
    case "8×":
      return "Would need 8 OAM GPUs on a UBB-class node";
    case "doesn't fit":
      if (key === "ryzen") {
        return "DOESN'T FIT — one Ryzen AI laptop";
      }
      if (key === "radeon") {
        return "DOESN'T FIT — one discrete Radeon";
      }
      if (key === "mi350p") {
        return "DOESN'T FIT — one MI350P";
      }
      return "DOESN'T FIT — one PCIe GPU or a Ryzen AI laptop";
    case "n/a":
      return "GPU-count fit does not apply";
  }
}

function nvfp4Note(key: PlatformKey): string {
  if (key === "mi300x" || key === "mi325x") {
    return "NVFP4→BF16 emulation possible in principle (AMD, other models); not tried. No native MXFP4";
  }
  if (key === "mi350x" || key === "mi355x") {
    return "Native MXFP4 yes. NVFP4 still BF16 emulation only; not tried for Nemotron";
  }
  if (key === "mi350p") {
    return "Native MXFP4 on CDNA4. NVFP4 still emulation-only; not tried. One PCIe card, not OAM scale-out";
  }
  return "NVFP4 emulation is not a documented path on that device";
}

function joinSentences(...parts: Array<string | undefined>): string {
  return parts
    .filter((part): part is string => Boolean(part && part.trim()))
    .join(". ");
}

function renderCell(
  cell: Cell,
  view: View,
  precision: string,
  key: PlatformKey,
) {
  const hypothetical = ["NYV", "NT", "NP", "NA", "Skip"].includes(cell.test);
  const headline =
    view === "fit" ? memoryLabel(cell.fit, hypothetical, key) : verdict(cell);
  const memory = memoryLabel(cell.fit, hypothetical, key);
  const extra = joinSentences(
    view === "fit" || view !== "both" || cell.fit === "doesn't fit"
      ? undefined
      : memory,
    cell.why ?? (view === "fit" ? undefined : detailLine(cell)),
    view === "fit" || cell.test === "Skip"
      ? undefined
      : precision === "NVFP4"
        ? nvfp4Note(key)
        : undefined,
  );

  return (
    <Stack gap={4}>
      <Text as="span" weight="bold">
        {headline}
      </Text>
      {extra ? (
        <Text as="span" size="small" tone="secondary">
          {extra}
        </Text>
      ) : null}
    </Stack>
  );
}

function matchesSlice(row: MatrixRow, slice: Slice): boolean {
  if (slice === "all") return true;
  if (slice === "executed") return row.executed;
  if (slice === "generative") {
    return ["nano30", "nano4", "lightning", "super", "ultra", "omni"].includes(
      row.family,
    );
  }
  if (slice === "retrieval") {
    return row.family === "embed" || row.family === "tools";
  }
  return !row.executed;
}

export default function CompatibilityMatrixCanvas() {
  const [view, setView] = useCanvasState<View>("view", "both");
  const [slice, setSlice] = useCanvasState<Slice>("slice", "all");

  const visible = ROWS.filter((row) => matchesSlice(row, slice));

  return (
    <Stack gap={20}>
      <Stack gap={6}>
        <H1>Nemotron × AMD hardware matrix</H1>
        <Text tone="secondary">
          16 August 2026. One product name, then extra rows for that
          product’s precisions — not extra models. Instinct OAM columns count
          GPUs on a scale-up node (1, 2, 4, or 8). MI350P, discrete Radeon,
          and a Ryzen AI laptop count as one device each. Only the MI300X
          column is from an executed run.
        </Text>
      </Stack>

      <Callout tone="neutral" title="Read the bold first line in each GPU cell. No color key required.">
        VALIDATED = executed; answers looked right. FAILED = executed; did
        not work. RAN — not validated = produced tokens, not a pass. NOT
        TESTED = not executed, and the weights would fit that device
        (fitting is still not a pass). DOESN'T FIT = weights exceed one
        PCIe GPU or a Ryzen AI laptop — that is not “not tested.” NO
        OFFICIAL FILE / NO SOFTWARE PATH = NVIDIA did not ship that
        checkpoint, or no Nemotron runtime is identified on that target.
      </Callout>

      <Grid columns={4} gap={16}>
        <Stat value="3" label="Validated language models on MI300X" tone="success" />
        <Stat value="4" label="Checkpoints that failed on MI300X" tone="warning" />
        <Stat value="1" label="GPU type executed: MI300X" />
        <Stat
          value="2 / 8 GPUs"
          label="Super / Ultra BF16 would need (memory only)"
        />
      </Grid>

      <Callout tone="warning" title="Only the MI300X column is an executed Instinct run">
        MI325X, MI350X, MI355X, MI350P, and discrete Radeon were not
        executed. Ryzen AI NPU was not executed. GGUF cells that say
        VALIDATED on the Ryzen AI laptop are CPU or iGPU Vulkan, not NPU.
        Super BF16, Ultra, and NVFP4 files were not downloaded. An MI300X
        result is not proof for another GPU.
      </Callout>

      <Row gap={8} wrap>
        <Pill active={slice === "all"} onClick={() => setSlice("all")}>
          All rows
        </Pill>
        <Pill active={slice === "executed"} onClick={() => setSlice("executed")}>
          Executed on MI300X
        </Pill>
        <Pill active={slice === "generative"} onClick={() => setSlice("generative")}>
          Generative LMs
        </Pill>
        <Pill active={slice === "retrieval"} onClick={() => setSlice("retrieval")}>
          Embed / parse / ASR / safety
        </Pill>
        <Pill active={slice === "unrun"} onClick={() => setSlice("unrun")}>
          Not downloaded
        </Pill>
      </Row>
      <Row gap={8} wrap>
        <Pill active={view === "both"} onClick={() => setView("both")}>
          Status, GPU count, NVFP4 note
        </Pill>
        <Pill active={view === "test"} onClick={() => setView("test")}>
          Status only
        </Pill>
        <Pill active={view === "fit"} onClick={() => setView("fit")}>
          GPU count only
        </Pill>
      </Row>

      <Table
        striped
        stickyHeader
        headers={["Model", "Precision", "Weight size", ...PLATFORM_HEADERS]}
        rows={visible.map((row, index) => [
          index > 0 && row.model === visible[index - 1].model ? "" : row.model,
          row.precision,
          row.weights,
          ...PLATFORM_KEYS.map((key) =>
            renderCell(row[key], view, row.precision, key),
          ),
        ])}
      />

      <Callout tone="info" title="NVIDIA 4-bit (NVFP4) is not an AMD format">
        Instinct does not run NVFP4 natively. MI350X/MI355X add MXFP4, which
        is a different 4-bit type. AMD has an emulation path (convert NVFP4
        to BF16 at compute time) that was shown on other models, not
        Nemotron. Emulation is not a pass in this table.
      </Callout>
    </Stack>
  );
}
