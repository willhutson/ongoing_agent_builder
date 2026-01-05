/**
 * Agent Tools
 *
 * Defines the tools available to agents for interacting with:
 * - File system
 * - Code search
 * - Git operations
 * - Database queries
 * - ERP-specific operations
 */

import type Anthropic from '@anthropic-ai/sdk';
import { agentLog } from '../lib/telemetry.js';

// ============================================
// TOOL CONTEXT
// ============================================

export interface ToolContext {
  jobId: string;
  organizationId: string;
  prisma: any;
  workingDirectory?: string;
}

// ============================================
// TOOL DEFINITIONS
// ============================================

const ALL_TOOLS: Record<string, Anthropic.Tool> = {
  read_file: {
    name: 'read_file',
    description: 'Read the contents of a file at the specified path',
    input_schema: {
      type: 'object' as const,
      properties: {
        file_path: {
          type: 'string',
          description: 'The path to the file to read',
        },
        start_line: {
          type: 'number',
          description: 'Optional starting line number',
        },
        end_line: {
          type: 'number',
          description: 'Optional ending line number',
        },
      },
      required: ['file_path'],
    },
  },

  write_file: {
    name: 'write_file',
    description: 'Write content to a file, creating it if it does not exist',
    input_schema: {
      type: 'object' as const,
      properties: {
        file_path: {
          type: 'string',
          description: 'The path to the file to write',
        },
        content: {
          type: 'string',
          description: 'The content to write to the file',
        },
      },
      required: ['file_path', 'content'],
    },
  },

  edit_file: {
    name: 'edit_file',
    description: 'Make a targeted edit to a file by replacing specific text',
    input_schema: {
      type: 'object' as const,
      properties: {
        file_path: {
          type: 'string',
          description: 'The path to the file to edit',
        },
        old_text: {
          type: 'string',
          description: 'The exact text to replace',
        },
        new_text: {
          type: 'string',
          description: 'The new text to insert',
        },
      },
      required: ['file_path', 'old_text', 'new_text'],
    },
  },

  search_files: {
    name: 'search_files',
    description: 'Search for files matching a glob pattern',
    input_schema: {
      type: 'object' as const,
      properties: {
        pattern: {
          type: 'string',
          description: 'Glob pattern to match files (e.g., "**/*.ts")',
        },
        directory: {
          type: 'string',
          description: 'Directory to search in',
        },
      },
      required: ['pattern'],
    },
  },

  search_code: {
    name: 'search_code',
    description: 'Search for text/regex patterns in code files',
    input_schema: {
      type: 'object' as const,
      properties: {
        pattern: {
          type: 'string',
          description: 'Text or regex pattern to search for',
        },
        file_pattern: {
          type: 'string',
          description: 'Optional glob pattern to filter files',
        },
        case_sensitive: {
          type: 'boolean',
          description: 'Whether search is case sensitive',
        },
      },
      required: ['pattern'],
    },
  },

  list_directory: {
    name: 'list_directory',
    description: 'List the contents of a directory',
    input_schema: {
      type: 'object' as const,
      properties: {
        path: {
          type: 'string',
          description: 'Directory path to list',
        },
        recursive: {
          type: 'boolean',
          description: 'Whether to list recursively',
        },
      },
      required: ['path'],
    },
  },

  run_command: {
    name: 'run_command',
    description: 'Run a shell command (limited to safe commands)',
    input_schema: {
      type: 'object' as const,
      properties: {
        command: {
          type: 'string',
          description: 'The command to run',
        },
        working_directory: {
          type: 'string',
          description: 'Working directory for the command',
        },
      },
      required: ['command'],
    },
  },

  git_status: {
    name: 'git_status',
    description: 'Get the current git status',
    input_schema: {
      type: 'object' as const,
      properties: {},
      required: [],
    },
  },

  git_diff: {
    name: 'git_diff',
    description: 'Get the git diff for current changes',
    input_schema: {
      type: 'object' as const,
      properties: {
        file_path: {
          type: 'string',
          description: 'Optional specific file to diff',
        },
      },
      required: [],
    },
  },

  create_branch: {
    name: 'create_branch',
    description: 'Create a new git branch',
    input_schema: {
      type: 'object' as const,
      properties: {
        branch_name: {
          type: 'string',
          description: 'Name for the new branch',
        },
      },
      required: ['branch_name'],
    },
  },

  commit_changes: {
    name: 'commit_changes',
    description: 'Stage and commit changes with a message',
    input_schema: {
      type: 'object' as const,
      properties: {
        message: {
          type: 'string',
          description: 'Commit message',
        },
        files: {
          type: 'array',
          items: { type: 'string' },
          description: 'Files to stage (optional, stages all if empty)',
        },
      },
      required: ['message'],
    },
  },

  query_database: {
    name: 'query_database',
    description: 'Query the ERP database using Prisma (read-only)',
    input_schema: {
      type: 'object' as const,
      properties: {
        model: {
          type: 'string',
          description: 'Prisma model name (e.g., "brief", "user")',
        },
        operation: {
          type: 'string',
          enum: ['findMany', 'findFirst', 'count'],
          description: 'Query operation',
        },
        where: {
          type: 'object',
          description: 'Where clause as JSON',
        },
        take: {
          type: 'number',
          description: 'Limit number of results',
        },
      },
      required: ['model', 'operation'],
    },
  },

  analyze_code: {
    name: 'analyze_code',
    description: 'Analyze code structure and dependencies',
    input_schema: {
      type: 'object' as const,
      properties: {
        file_path: {
          type: 'string',
          description: 'File to analyze',
        },
        analysis_type: {
          type: 'string',
          enum: ['imports', 'exports', 'functions', 'types', 'dependencies'],
          description: 'Type of analysis',
        },
      },
      required: ['file_path', 'analysis_type'],
    },
  },
};

// ============================================
// TOOL FILTERING
// ============================================

/**
 * Get tool definitions filtered by allowed tool names
 */
export function getToolDefinitions(allowedTools: string[]): Anthropic.Tool[] {
  const tools: Anthropic.Tool[] = [];

  for (const toolName of allowedTools) {
    if (ALL_TOOLS[toolName]) {
      tools.push(ALL_TOOLS[toolName]);
    }
  }

  return tools;
}

/**
 * Get all available tool names
 */
export function getAvailableTools(): string[] {
  return Object.keys(ALL_TOOLS);
}

// ============================================
// TOOL EXECUTION
// ============================================

/**
 * Execute a tool call
 */
export async function executeToolCall(
  toolName: string,
  input: Record<string, unknown>,
  context: ToolContext
): Promise<unknown> {
  await agentLog(context.jobId, 'DEBUG', `Executing tool: ${toolName}`, { input });

  switch (toolName) {
    case 'read_file':
      return executeReadFile(input, context);

    case 'write_file':
      return executeWriteFile(input, context);

    case 'edit_file':
      return executeEditFile(input, context);

    case 'search_files':
      return executeSearchFiles(input, context);

    case 'search_code':
      return executeSearchCode(input, context);

    case 'list_directory':
      return executeListDirectory(input, context);

    case 'run_command':
      return executeCommand(input, context);

    case 'git_status':
      return executeGitStatus(context);

    case 'git_diff':
      return executeGitDiff(input, context);

    case 'query_database':
      return executeQueryDatabase(input, context);

    case 'analyze_code':
      return executeAnalyzeCode(input, context);

    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}

// ============================================
// TOOL IMPLEMENTATIONS
// ============================================

async function executeReadFile(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string> {
  const { file_path, start_line, end_line } = input as {
    file_path: string;
    start_line?: number;
    end_line?: number;
  };

  // In ERP context, use fs
  const fs = await import('fs/promises');
  const path = await import('path');

  const fullPath = path.resolve(context.workingDirectory || process.cwd(), file_path);
  const content = await fs.readFile(fullPath, 'utf-8');

  if (start_line !== undefined || end_line !== undefined) {
    const lines = content.split('\n');
    const start = (start_line || 1) - 1;
    const end = end_line || lines.length;
    return lines.slice(start, end).join('\n');
  }

  return content;
}

async function executeWriteFile(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string> {
  const { file_path, content } = input as {
    file_path: string;
    content: string;
  };

  const fs = await import('fs/promises');
  const path = await import('path');

  const fullPath = path.resolve(context.workingDirectory || process.cwd(), file_path);

  // Ensure directory exists
  await fs.mkdir(path.dirname(fullPath), { recursive: true });
  await fs.writeFile(fullPath, content, 'utf-8');

  return `File written: ${file_path}`;
}

async function executeEditFile(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string> {
  const { file_path, old_text, new_text } = input as {
    file_path: string;
    old_text: string;
    new_text: string;
  };

  const fs = await import('fs/promises');
  const path = await import('path');

  const fullPath = path.resolve(context.workingDirectory || process.cwd(), file_path);
  const content = await fs.readFile(fullPath, 'utf-8');

  if (!content.includes(old_text)) {
    throw new Error(`Text not found in file: "${old_text.slice(0, 50)}..."`);
  }

  const newContent = content.replace(old_text, new_text);
  await fs.writeFile(fullPath, newContent, 'utf-8');

  return `File edited: ${file_path}`;
}

async function executeSearchFiles(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string[]> {
  const { pattern, directory } = input as {
    pattern: string;
    directory?: string;
  };

  // Use glob
  const { glob } = await import('glob');
  const path = await import('path');

  const cwd = path.resolve(context.workingDirectory || process.cwd(), directory || '.');
  const files = await glob(pattern, { cwd, nodir: true });

  return files.slice(0, 100); // Limit results
}

async function executeSearchCode(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<Array<{ file: string; line: number; content: string }>> {
  const { pattern, file_pattern, case_sensitive } = input as {
    pattern: string;
    file_pattern?: string;
    case_sensitive?: boolean;
  };

  // Simple implementation - in production, use ripgrep
  const { glob } = await import('glob');
  const fs = await import('fs/promises');
  const path = await import('path');

  const cwd = context.workingDirectory || process.cwd();
  const files = await glob(file_pattern || '**/*.{ts,tsx,js,jsx}', {
    cwd,
    nodir: true,
    ignore: ['**/node_modules/**', '**/dist/**'],
  });

  const results: Array<{ file: string; line: number; content: string }> = [];
  const regex = new RegExp(pattern, case_sensitive ? 'g' : 'gi');

  for (const file of files.slice(0, 50)) {
    try {
      const content = await fs.readFile(path.join(cwd, file), 'utf-8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          results.push({
            file,
            line: i + 1,
            content: lines[i].trim(),
          });
        }
        regex.lastIndex = 0; // Reset regex state
      }
    } catch {
      // Skip unreadable files
    }

    if (results.length >= 50) break;
  }

  return results;
}

async function executeListDirectory(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string[]> {
  const { path: dirPath, recursive } = input as {
    path: string;
    recursive?: boolean;
  };

  const fs = await import('fs/promises');
  const path = await import('path');

  const fullPath = path.resolve(context.workingDirectory || process.cwd(), dirPath);

  if (recursive) {
    const { glob } = await import('glob');
    return glob('**/*', { cwd: fullPath, nodir: false });
  }

  const entries = await fs.readdir(fullPath, { withFileTypes: true });
  return entries.map((e) => (e.isDirectory() ? `${e.name}/` : e.name));
}

async function executeCommand(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string> {
  const { command, working_directory } = input as {
    command: string;
    working_directory?: string;
  };

  // Allowlist of safe commands
  const safeCommands = ['npm', 'pnpm', 'yarn', 'tsc', 'eslint', 'prettier', 'jest', 'vitest'];
  const firstWord = command.split(' ')[0];

  if (!safeCommands.includes(firstWord)) {
    throw new Error(`Command not allowed: ${firstWord}`);
  }

  const { exec } = await import('child_process');
  const { promisify } = await import('util');
  const execAsync = promisify(exec);
  const path = await import('path');

  const cwd = path.resolve(
    context.workingDirectory || process.cwd(),
    working_directory || '.'
  );

  const { stdout, stderr } = await execAsync(command, { cwd, timeout: 60000 });
  return stdout + (stderr ? `\nStderr: ${stderr}` : '');
}

async function executeGitStatus(context: ToolContext): Promise<string> {
  const { exec } = await import('child_process');
  const { promisify } = await import('util');
  const execAsync = promisify(exec);

  const { stdout } = await execAsync('git status --porcelain', {
    cwd: context.workingDirectory || process.cwd(),
  });

  return stdout || 'Working directory clean';
}

async function executeGitDiff(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<string> {
  const { file_path } = input as { file_path?: string };

  const { exec } = await import('child_process');
  const { promisify } = await import('util');
  const execAsync = promisify(exec);

  const cmd = file_path ? `git diff -- ${file_path}` : 'git diff';
  const { stdout } = await execAsync(cmd, {
    cwd: context.workingDirectory || process.cwd(),
  });

  return stdout || 'No changes';
}

async function executeQueryDatabase(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<unknown> {
  const { model, operation, where, take } = input as {
    model: string;
    operation: 'findMany' | 'findFirst' | 'count';
    where?: Record<string, unknown>;
    take?: number;
  };

  const prisma = context.prisma;
  if (!prisma || !prisma[model]) {
    throw new Error(`Unknown model: ${model}`);
  }

  // Always filter by organization for security
  const whereClause = {
    ...where,
    organizationId: context.organizationId,
  };

  const result = await prisma[model][operation]({
    where: whereClause,
    ...(take && operation === 'findMany' ? { take } : {}),
  });

  return result;
}

async function executeAnalyzeCode(
  input: Record<string, unknown>,
  context: ToolContext
): Promise<unknown> {
  const { file_path, analysis_type } = input as {
    file_path: string;
    analysis_type: string;
  };

  const fs = await import('fs/promises');
  const path = await import('path');

  const fullPath = path.resolve(context.workingDirectory || process.cwd(), file_path);
  const content = await fs.readFile(fullPath, 'utf-8');

  switch (analysis_type) {
    case 'imports': {
      const imports = content.match(/^import .+ from ['"].+['"]/gm) || [];
      return imports;
    }
    case 'exports': {
      const exports = content.match(/^export (default |const |function |class |type |interface ).+/gm) || [];
      return exports;
    }
    case 'functions': {
      const functions = content.match(/(async )?function \w+|const \w+ = (async )?\(/gm) || [];
      return functions;
    }
    case 'types': {
      const types = content.match(/^(type|interface) \w+/gm) || [];
      return types;
    }
    default:
      throw new Error(`Unknown analysis type: ${analysis_type}`);
  }
}
