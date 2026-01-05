/**
 * Agent Executor
 *
 * Executes agents with the Claude API, managing:
 * - Tool execution
 * - Conversation flow
 * - Result extraction
 * - Error handling
 */

import Anthropic from '@anthropic-ai/sdk';
import type {
  AgentJob,
  AgentArtifact,
  JobResult,
  ArtifactType,
} from '../types/index.js';
import { getConfig, MODEL_IDS, MODEL_LIMITS } from '../config/index.js';
import { agentLog } from '../lib/telemetry.js';
import { getAgentDefinition } from '../agents/registry.js';
import { executeToolCall, getToolDefinitions } from '../tools/index.js';

// ============================================
// EXECUTOR
// ============================================

export class AgentExecutor {
  private client: Anthropic;

  constructor(private prisma: any) {
    const config = getConfig();
    this.client = new Anthropic({
      apiKey: config.ANTHROPIC_API_KEY,
    });
  }

  /**
   * Execute an agent job
   */
  async execute(job: AgentJob, signal?: AbortSignal): Promise<JobResult> {
    const agentDef = getAgentDefinition(job.agentType);
    const modelId = MODEL_IDS[job.model];
    const limits = MODEL_LIMITS[job.model];

    await agentLog(job.id, 'INFO', `Starting ${job.agentType} agent with ${job.model}`, {
      modelId,
      maxTokens: limits.maxTokens,
    });

    // Get the issue details
    const issue = await this.prisma.agentIssue.findUnique({
      where: { id: job.issueId },
    });

    if (!issue) {
      throw new Error(`Issue ${job.issueId} not found`);
    }

    // Build the system prompt
    const systemPrompt = this.buildSystemPrompt(agentDef, issue);

    // Get tool definitions for this agent
    const tools = getToolDefinitions(job.config.tools || agentDef.tools);

    // Execute the agent loop
    const artifacts: AgentArtifact[] = [];
    const messages: Anthropic.MessageParam[] = [
      {
        role: 'user',
        content: this.buildUserPrompt(issue),
      },
    ];

    let continueLoop = true;
    let iterations = 0;
    const maxIterations = 20;

    while (continueLoop && iterations < maxIterations) {
      iterations++;

      // Check for abort
      if (signal?.aborted) {
        throw new Error('Job cancelled');
      }

      await agentLog(job.id, 'DEBUG', `Iteration ${iterations}`, {
        messageCount: messages.length,
      });

      // Call Claude
      const response = await this.client.messages.create({
        model: modelId,
        max_tokens: limits.maxTokens,
        system: systemPrompt,
        tools: tools as any,
        messages,
      });

      // Process the response
      const assistantContent: Anthropic.ContentBlock[] = [];
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const block of response.content) {
        if (block.type === 'text') {
          assistantContent.push(block);
          await agentLog(job.id, 'INFO', 'Agent thinking', {
            text: block.text.slice(0, 200),
          });
        } else if (block.type === 'tool_use') {
          assistantContent.push(block);

          await agentLog(job.id, 'INFO', `Tool call: ${block.name}`, {
            input: block.input,
          });

          // Execute the tool
          try {
            const result = await executeToolCall(
              block.name,
              block.input as Record<string, unknown>,
              {
                jobId: job.id,
                organizationId: job.organizationId,
                prisma: this.prisma,
              }
            );

            toolResults.push({
              type: 'tool_result',
              tool_use_id: block.id,
              content: typeof result === 'string' ? result : JSON.stringify(result),
            });

            // Track artifacts from tool calls
            if (block.name === 'edit_file' || block.name === 'write_file') {
              const artifact = await this.createArtifact(job.id, 'CODE_CHANGE', block, result);
              artifacts.push(artifact);
            }

          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            await agentLog(job.id, 'WARN', `Tool error: ${block.name}`, { error: errorMessage });

            toolResults.push({
              type: 'tool_result',
              tool_use_id: block.id,
              content: `Error: ${errorMessage}`,
              is_error: true,
            });
          }
        }
      }

      // Add assistant message
      messages.push({
        role: 'assistant',
        content: assistantContent,
      });

      // Check if we should continue
      if (response.stop_reason === 'end_turn') {
        continueLoop = false;
      } else if (response.stop_reason === 'tool_use' && toolResults.length > 0) {
        // Add tool results and continue
        messages.push({
          role: 'user',
          content: toolResults,
        });
      } else {
        continueLoop = false;
      }
    }

    // Extract final result
    const lastMessage = messages[messages.length - 1];
    let summary = 'Agent completed task';

    if (lastMessage.role === 'assistant' && Array.isArray(lastMessage.content)) {
      const textBlock = lastMessage.content.find((b): b is Anthropic.TextBlock => b.type === 'text');
      if (textBlock) {
        summary = textBlock.text;
      }
    }

    await agentLog(job.id, 'INFO', 'Agent completed', {
      iterations,
      artifactCount: artifacts.length,
    });

    return {
      summary,
      artifacts,
      recommendations: this.extractRecommendations(summary),
    };
  }

  /**
   * Build the system prompt for the agent
   */
  private buildSystemPrompt(agentDef: any, issue: any): string {
    return `${agentDef.systemPrompt}

## Current Issue
- ID: ${issue.id}
- Type: ${issue.type}
- Priority: ${issue.priority}
- Module: ${issue.context?.module || 'unknown'}

## Guidelines
1. Analyze the issue thoroughly before making changes
2. Use tools to explore the codebase and understand context
3. Make minimal, focused changes
4. Document your reasoning
5. Suggest follow-up actions if needed

## Output Format
When complete, provide:
1. Summary of what was done
2. List of changes made
3. Recommendations for next steps (if any)`;
  }

  /**
   * Build the user prompt with issue details
   */
  private buildUserPrompt(issue: any): string {
    return `# Issue: ${issue.title}

## Description
${issue.description}

${issue.context?.errorLogs ? `## Error Logs\n\`\`\`\n${issue.context.errorLogs}\n\`\`\`` : ''}

${issue.context?.affectedFiles?.length ? `## Potentially Affected Files\n${issue.context.affectedFiles.map((f: string) => `- ${f}`).join('\n')}` : ''}

Please analyze this issue and take appropriate action.`;
  }

  /**
   * Create an artifact record
   */
  private async createArtifact(
    jobId: string,
    type: ArtifactType,
    toolCall: Anthropic.ToolUseBlock,
    result: unknown
  ): Promise<AgentArtifact> {
    const input = toolCall.input as Record<string, unknown>;

    return this.prisma.agentArtifact.create({
      data: {
        jobId,
        type,
        name: toolCall.name,
        content: JSON.stringify(result),
        filePath: input.file_path as string | undefined,
        metadata: { toolInput: input },
      },
    });
  }

  /**
   * Extract recommendations from summary text
   */
  private extractRecommendations(summary: string): string[] {
    const recommendations: string[] = [];

    // Look for common patterns
    const patterns = [
      /recommend(?:ed|s)?\s*(?:to\s+)?([^.]+)/gi,
      /suggest(?:ed|s)?\s*(?:to\s+)?([^.]+)/gi,
      /should\s+([^.]+)/gi,
      /next steps?:?\s*([^.]+)/gi,
    ];

    for (const pattern of patterns) {
      const matches = summary.matchAll(pattern);
      for (const match of matches) {
        if (match[1] && match[1].length < 200) {
          recommendations.push(match[1].trim());
        }
      }
    }

    return recommendations.slice(0, 5);
  }
}
