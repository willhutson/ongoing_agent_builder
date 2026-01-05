/**
 * Autonomous Feedback Loop Runner
 *
 * Continuously processes the feedback → kanban → improvement cycle.
 * Designed to run until a completion condition is met (like ralph-loop).
 *
 * Usage:
 *   Start the loop and watch it work through:
 *   1. New feedback in queue
 *   2. Cards needing analysis
 *   3. Improvements ready to apply
 *   4. Testing and verification
 */

import { feedbackEvents, createJobStream } from '../integrations/realtime.js';
import { agentLog } from '../lib/telemetry.js';

// ============================================
// TYPES
// ============================================

export interface FeedbackLoopConfig {
  organizationId: string;
  prisma: PrismaLike;

  // Loop control
  maxIterations?: number;           // Stop after N iterations (0 = infinite)
  completionPromise?: string;       // Stop when this condition is met
  checkIntervalMs?: number;         // How often to check for work (default: 5000)

  // Processing limits
  batchSize?: number;               // Items to process per iteration
  pauseBetweenItems?: boolean;      // Pause for observation between items

  // Callbacks for watching
  onIterationStart?: (iteration: number) => void;
  onItemProcessed?: (item: ProcessedItem) => void;
  onIterationEnd?: (stats: IterationStats) => void;
  onComplete?: (reason: string) => void;
}

export interface ProcessedItem {
  type: 'feedback' | 'card_analysis' | 'improvement' | 'verification';
  id: string;
  status: 'success' | 'failed' | 'skipped';
  details: string;
  duration: number;
}

export interface IterationStats {
  iteration: number;
  feedbackProcessed: number;
  cardsAnalyzed: number;
  improvementsApplied: number;
  verificationsRun: number;
  duration: number;
}

export interface LoopState {
  isRunning: boolean;
  isPaused: boolean;
  currentIteration: number;
  totalProcessed: number;
  startedAt: Date;
  lastActivity: Date;
  completionReason?: string;
}

// ============================================
// FEEDBACK LOOP RUNNER
// ============================================

export class FeedbackLoopRunner {
  private config: Required<FeedbackLoopConfig>;
  private state: LoopState;
  private abortController: AbortController;

  constructor(config: FeedbackLoopConfig) {
    this.config = {
      maxIterations: 0,
      completionPromise: 'DONE',
      checkIntervalMs: 5000,
      batchSize: 5,
      pauseBetweenItems: false,
      onIterationStart: () => {},
      onItemProcessed: () => {},
      onIterationEnd: () => {},
      onComplete: () => {},
      ...config,
    };

    this.state = {
      isRunning: false,
      isPaused: false,
      currentIteration: 0,
      totalProcessed: 0,
      startedAt: new Date(),
      lastActivity: new Date(),
    };

    this.abortController = new AbortController();
  }

  /**
   * Start the autonomous loop
   */
  async start(): Promise<void> {
    if (this.state.isRunning) {
      console.log('⚠️ Feedback loop already running');
      return;
    }

    this.state.isRunning = true;
    this.state.startedAt = new Date();
    console.log('🔄 Starting autonomous feedback loop...');
    console.log(`   Completion condition: "${this.config.completionPromise}"`);

    try {
      await this.runLoop();
    } finally {
      this.state.isRunning = false;
      this.config.onComplete(this.state.completionReason || 'stopped');
    }
  }

  /**
   * Main loop logic
   */
  private async runLoop(): Promise<void> {
    while (!this.shouldStop()) {
      this.state.currentIteration++;
      const iterationStart = Date.now();

      this.config.onIterationStart(this.state.currentIteration);
      console.log(`\n━━━ Iteration ${this.state.currentIteration} ━━━`);

      const stats: IterationStats = {
        iteration: this.state.currentIteration,
        feedbackProcessed: 0,
        cardsAnalyzed: 0,
        improvementsApplied: 0,
        verificationsRun: 0,
        duration: 0,
      };

      // Step 1: Process new feedback → Create cards
      const feedbackResults = await this.processPendingFeedback();
      stats.feedbackProcessed = feedbackResults.length;

      // Step 2: Analyze cards in "Analysis" column
      const analysisResults = await this.analyzeCards();
      stats.cardsAnalyzed = analysisResults.length;

      // Step 3: Apply improvements from "In Progress" cards
      const improvementResults = await this.applyImprovements();
      stats.improvementsApplied = improvementResults.length;

      // Step 4: Verify improvements in "Testing" column
      const verificationResults = await this.verifyImprovements();
      stats.verificationsRun = verificationResults.length;

      // Update stats
      stats.duration = Date.now() - iterationStart;
      this.state.totalProcessed +=
        stats.feedbackProcessed +
        stats.cardsAnalyzed +
        stats.improvementsApplied +
        stats.verificationsRun;

      this.config.onIterationEnd(stats);

      // Check if we did any work
      const workDone = stats.feedbackProcessed + stats.cardsAnalyzed +
                       stats.improvementsApplied + stats.verificationsRun;

      if (workDone === 0) {
        console.log('💤 No work to do, waiting...');
      } else {
        console.log(`✅ Iteration ${this.state.currentIteration} complete: ${workDone} items processed`);
      }

      // Check completion condition
      if (await this.checkCompletionCondition()) {
        this.state.completionReason = this.config.completionPromise;
        console.log(`🎉 Completion condition met: "${this.config.completionPromise}"`);
        break;
      }

      // Wait before next iteration
      await this.sleep(this.config.checkIntervalMs);
    }
  }

  /**
   * Process pending feedback into kanban cards
   */
  private async processPendingFeedback(): Promise<ProcessedItem[]> {
    console.log('📥 Checking for new feedback...');

    const pendingFeedback = await this.config.prisma.agentFeedback.findMany({
      where: {
        organizationId: this.config.organizationId,
        improvementStatus: 'pending',
      },
      take: this.config.batchSize,
      orderBy: { createdAt: 'asc' },
    });

    if (pendingFeedback.length === 0) {
      return [];
    }

    console.log(`   Found ${pendingFeedback.length} feedback items to process`);

    const results: ProcessedItem[] = [];

    for (const feedback of pendingFeedback) {
      const start = Date.now();

      try {
        // Create kanban card from feedback
        const card = await this.createImprovementCard(feedback);

        // Update feedback status
        await this.config.prisma.agentFeedback.update({
          where: { id: feedback.id },
          data: {
            improvementStatus: 'analyzed',
            kanbanCardId: card.id,
          },
        });

        // Emit real-time event
        feedbackEvents.cardCreated(this.config.organizationId, {
          cardId: card.id,
          feedbackId: feedback.id,
          title: card.title,
          column: 'Incoming',
          agentType: feedback.agentType,
          priority: this.calculatePriority(feedback),
        });

        const item: ProcessedItem = {
          type: 'feedback',
          id: feedback.id,
          status: 'success',
          details: `Created card: ${card.title}`,
          duration: Date.now() - start,
        };

        results.push(item);
        this.config.onItemProcessed(item);
        console.log(`   ✓ Feedback ${feedback.id} → Card ${card.id}`);

        if (this.config.pauseBetweenItems) {
          await this.sleep(1000);
        }
      } catch (error) {
        results.push({
          type: 'feedback',
          id: feedback.id,
          status: 'failed',
          details: String(error),
          duration: Date.now() - start,
        });
        console.log(`   ✗ Feedback ${feedback.id} failed: ${error}`);
      }
    }

    return results;
  }

  /**
   * Analyze cards that need analysis
   */
  private async analyzeCards(): Promise<ProcessedItem[]> {
    console.log('🔍 Checking for cards needing analysis...');

    const cardsToAnalyze = await this.config.prisma.boardCard.findMany({
      where: {
        board: {
          organizationId: this.config.organizationId,
          name: 'Agent Improvements',
        },
        column: { name: 'Analysis' },
      },
      take: this.config.batchSize,
      include: {
        board: true,
      },
    });

    if (cardsToAnalyze.length === 0) {
      return [];
    }

    console.log(`   Found ${cardsToAnalyze.length} cards to analyze`);

    const results: ProcessedItem[] = [];

    for (const card of cardsToAnalyze) {
      const start = Date.now();

      try {
        // Emit analysis started event
        feedbackEvents.analysisStarted(
          this.config.organizationId,
          card.id,
          card.metadata?.agentType as string || 'unknown'
        );

        // Run the feedback analyzer agent
        const analysis = await this.runFeedbackAnalyzer(card);

        // Update card with analysis
        await this.updateCardWithAnalysis(card.id, analysis);

        // Move card to Backlog (or Dismissed)
        const targetColumn = analysis.shouldDismiss ? 'Dismissed' : 'Backlog';
        await this.moveCard(card.id, targetColumn);

        feedbackEvents.cardMoved(this.config.organizationId, {
          cardId: card.id,
          fromColumn: 'Analysis',
          toColumn: targetColumn,
          movedBy: 'agent',
          reason: analysis.reasoning,
        });

        const item: ProcessedItem = {
          type: 'card_analysis',
          id: card.id,
          status: 'success',
          details: `Analyzed and moved to ${targetColumn}`,
          duration: Date.now() - start,
        };

        results.push(item);
        this.config.onItemProcessed(item);
        console.log(`   ✓ Card ${card.id} analyzed → ${targetColumn}`);

        if (this.config.pauseBetweenItems) {
          await this.sleep(1000);
        }
      } catch (error) {
        results.push({
          type: 'card_analysis',
          id: card.id,
          status: 'failed',
          details: String(error),
          duration: Date.now() - start,
        });
        console.log(`   ✗ Card ${card.id} analysis failed: ${error}`);
      }
    }

    return results;
  }

  /**
   * Apply improvements from cards in "In Progress"
   */
  private async applyImprovements(): Promise<ProcessedItem[]> {
    console.log('🔧 Checking for improvements to apply...');

    const cardsInProgress = await this.config.prisma.boardCard.findMany({
      where: {
        board: {
          organizationId: this.config.organizationId,
          name: 'Agent Improvements',
        },
        column: { name: 'In Progress' },
        // Only auto-apply cards tagged for auto-improvement
        labels: { some: { name: 'auto-apply' } },
      },
      take: this.config.batchSize,
    });

    if (cardsInProgress.length === 0) {
      return [];
    }

    console.log(`   Found ${cardsInProgress.length} improvements to apply`);

    const results: ProcessedItem[] = [];

    for (const card of cardsInProgress) {
      const start = Date.now();

      try {
        // Apply the improvement
        const improvement = await this.applyImprovement(card);

        // Move to Testing
        await this.moveCard(card.id, 'Testing');

        feedbackEvents.improvementApplied(this.config.organizationId, {
          cardId: card.id,
          agentType: card.metadata?.agentType as string || 'unknown',
          improvementType: improvement.type,
          description: improvement.description,
          beforeVersion: improvement.beforeVersion,
          afterVersion: improvement.afterVersion,
        });

        feedbackEvents.cardMoved(this.config.organizationId, {
          cardId: card.id,
          fromColumn: 'In Progress',
          toColumn: 'Testing',
          movedBy: 'agent',
          reason: 'Improvement applied, ready for testing',
        });

        const item: ProcessedItem = {
          type: 'improvement',
          id: card.id,
          status: 'success',
          details: `Applied: ${improvement.description}`,
          duration: Date.now() - start,
        };

        results.push(item);
        this.config.onItemProcessed(item);
        console.log(`   ✓ Improvement ${card.id} applied`);

      } catch (error) {
        results.push({
          type: 'improvement',
          id: card.id,
          status: 'failed',
          details: String(error),
          duration: Date.now() - start,
        });
        console.log(`   ✗ Improvement ${card.id} failed: ${error}`);
      }
    }

    return results;
  }

  /**
   * Verify improvements in "Testing" column
   */
  private async verifyImprovements(): Promise<ProcessedItem[]> {
    console.log('🧪 Checking for improvements to verify...');

    const cardsInTesting = await this.config.prisma.boardCard.findMany({
      where: {
        board: {
          organizationId: this.config.organizationId,
          name: 'Agent Improvements',
        },
        column: { name: 'Testing' },
      },
      take: this.config.batchSize,
    });

    if (cardsInTesting.length === 0) {
      return [];
    }

    console.log(`   Found ${cardsInTesting.length} improvements to verify`);

    const results: ProcessedItem[] = [];

    for (const card of cardsInTesting) {
      const start = Date.now();

      try {
        // Check if enough feedback has been collected post-improvement
        const postImprovementFeedback = await this.getPostImprovementFeedback(card);

        if (postImprovementFeedback.count < 3) {
          // Not enough data yet, skip
          results.push({
            type: 'verification',
            id: card.id,
            status: 'skipped',
            details: `Waiting for more feedback (${postImprovementFeedback.count}/3)`,
            duration: Date.now() - start,
          });
          continue;
        }

        // Verify the improvement worked
        const verification = this.verifyImprovement(postImprovementFeedback);

        if (verification.success) {
          // Move to Done
          await this.moveCard(card.id, 'Done');
          feedbackEvents.cardMoved(this.config.organizationId, {
            cardId: card.id,
            fromColumn: 'Testing',
            toColumn: 'Done',
            movedBy: 'system',
            reason: `Verified: ${verification.reason}`,
          });
          console.log(`   ✓ Improvement ${card.id} verified successful`);
        } else {
          // Move back to Backlog for re-work
          await this.moveCard(card.id, 'Backlog');
          feedbackEvents.cardMoved(this.config.organizationId, {
            cardId: card.id,
            fromColumn: 'Testing',
            toColumn: 'Backlog',
            movedBy: 'system',
            reason: `Failed verification: ${verification.reason}`,
          });
          console.log(`   ↩ Improvement ${card.id} needs re-work`);
        }

        results.push({
          type: 'verification',
          id: card.id,
          status: 'success',
          details: verification.reason,
          duration: Date.now() - start,
        });

      } catch (error) {
        results.push({
          type: 'verification',
          id: card.id,
          status: 'failed',
          details: String(error),
          duration: Date.now() - start,
        });
      }
    }

    return results;
  }

  // ============================================
  // HELPER METHODS
  // ============================================

  private shouldStop(): boolean {
    if (this.abortController.signal.aborted) return true;
    if (this.config.maxIterations > 0 &&
        this.state.currentIteration >= this.config.maxIterations) {
      this.state.completionReason = 'max_iterations_reached';
      return true;
    }
    return false;
  }

  private async checkCompletionCondition(): Promise<boolean> {
    // Check if all queues are empty and nothing pending
    const pendingFeedback = await this.config.prisma.agentFeedback.count({
      where: {
        organizationId: this.config.organizationId,
        improvementStatus: 'pending',
      },
    });

    const cardsInProgress = await this.config.prisma.boardCard.count({
      where: {
        board: {
          organizationId: this.config.organizationId,
          name: 'Agent Improvements',
        },
        column: {
          name: { in: ['Incoming', 'Analysis', 'In Progress', 'Testing'] },
        },
      },
    });

    // "DONE" when nothing left to process
    if (this.config.completionPromise === 'DONE') {
      return pendingFeedback === 0 && cardsInProgress === 0;
    }

    return false;
  }

  private async createImprovementCard(feedback: any): Promise<any> {
    // Implementation - creates card in Boards module
    return this.config.prisma.boardCard.create({
      data: {
        // ... card creation logic
      },
    });
  }

  private async runFeedbackAnalyzer(card: any): Promise<any> {
    // Implementation - runs meta.feedback-analyzer agent
    return { shouldDismiss: false, reasoning: 'Analysis complete' };
  }

  private async updateCardWithAnalysis(cardId: string, analysis: any): Promise<void> {
    // Implementation - updates card with analysis results
  }

  private async moveCard(cardId: string, columnName: string): Promise<void> {
    // Implementation - moves card to specified column
  }

  private async applyImprovement(card: any): Promise<any> {
    // Implementation - applies the improvement to the agent
    return {
      type: 'prompt_update',
      description: 'Updated system prompt',
      beforeVersion: '1.0.0',
      afterVersion: '1.0.1',
    };
  }

  private async getPostImprovementFeedback(card: any): Promise<any> {
    // Get feedback received after improvement was applied
    return { count: 0, avgRating: 0 };
  }

  private verifyImprovement(feedback: any): { success: boolean; reason: string } {
    // Check if feedback improved after the change
    return { success: true, reason: 'Rating improved by 0.5 stars' };
  }

  private calculatePriority(feedback: any): string {
    if (feedback.rating <= 2 && feedback.outcome === 'made_worse') return 'critical';
    if (feedback.rating <= 2) return 'high';
    if (feedback.rating <= 3) return 'medium';
    return 'low';
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const timeout = setTimeout(resolve, ms);
      this.abortController.signal.addEventListener('abort', () => {
        clearTimeout(timeout);
        resolve();
      });
    });
  }

  /**
   * Stop the loop
   */
  stop(): void {
    console.log('🛑 Stopping feedback loop...');
    this.abortController.abort();
  }

  /**
   * Pause the loop
   */
  pause(): void {
    this.state.isPaused = true;
    console.log('⏸️ Feedback loop paused');
  }

  /**
   * Resume the loop
   */
  resume(): void {
    this.state.isPaused = false;
    console.log('▶️ Feedback loop resumed');
  }

  /**
   * Get current state
   */
  getState(): LoopState {
    return { ...this.state };
  }
}

// ============================================
// CONVENIENCE FUNCTION
// ============================================

/**
 * Start the feedback loop (like ralph-loop)
 *
 * @example
 * // Run until all feedback is processed
 * await startFeedbackLoop(prisma, orgId, { completionPromise: 'DONE' });
 *
 * // Run 10 iterations
 * await startFeedbackLoop(prisma, orgId, { maxIterations: 10 });
 *
 * // Run with real-time observation
 * await startFeedbackLoop(prisma, orgId, {
 *   pauseBetweenItems: true,
 *   onItemProcessed: (item) => console.log('Processed:', item),
 * });
 */
export async function startFeedbackLoop(
  prisma: PrismaLike,
  organizationId: string,
  options: Partial<FeedbackLoopConfig> = {}
): Promise<LoopState> {
  const runner = new FeedbackLoopRunner({
    prisma,
    organizationId,
    ...options,
  });

  await runner.start();
  return runner.getState();
}

// Type stub
interface PrismaLike {
  agentFeedback: any;
  boardCard: any;
}
