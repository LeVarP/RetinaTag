/**
 * Labeling hook for updating B-scan labels with optimistic UI.
 * Handles health/pathology updates and full unlabel operation.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Label, type BScan, type BScanPathologyUpdate } from '@/types';

interface UseLabelingProps {
  scanId: string;
  bscanId: number | undefined;
  currentIndex: number;
  onSuccess?: () => void;
}

/**
 * Hook for managing label updates with optimistic UI.
 */
export function useLabeling({ scanId, bscanId, currentIndex, onSuccess }: UseLabelingProps) {
  const queryClient = useQueryClient();
  const queryKey = ['bscan', scanId, currentIndex] as const;

  const updateLabelMutation = useMutation({
    mutationFn: ({ healthy }: { healthy: 0 | 1 }) => {
      if (!bscanId) {
        return Promise.reject(new Error('No B-scan ID'));
      }
      return api.updateHealth(bscanId, { healthy });
    },
    onMutate: async ({ healthy }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey });

      // Snapshot previous value
      const previousBScan = queryClient.getQueryData<BScan>(queryKey);

      // Optimistically update
      if (previousBScan) {
        queryClient.setQueryData(queryKey, {
          ...previousBScan,
          label: healthy === 1 ? Label.Healthy : Label.Unhealthy,
          healthy,
          is_labeled: true,
        });
      }

      return { previousBScan, queryKey };
    },
    onError: (err, _variables, context) => {
      // Revert on error
      if (context?.previousBScan) {
        queryClient.setQueryData(context.queryKey, context.previousBScan);
      }
      console.error('Failed to update label:', err);
    },
    onSuccess: (data) => {
      // Update cache with server response using the index-based key
      queryClient.setQueryData(['bscan', scanId, currentIndex], data);

      // Invalidate scans list to refresh statistics
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      queryClient.invalidateQueries({ queryKey: ['scan', scanId, 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['globalStats'] });

      // Call auto-advance callback
      if (onSuccess) {
        onSuccess();
      }
    },
  });

  const updatePathologyMutation = useMutation({
    mutationFn: (pathologyUpdate: BScanPathologyUpdate) => {
      if (!bscanId) {
        return Promise.reject(new Error('No B-scan ID'));
      }
      return api.updatePathology(bscanId, pathologyUpdate);
    },
    onMutate: async (pathologyUpdate) => {
      await queryClient.cancelQueries({ queryKey });
      const previousBScan = queryClient.getQueryData<BScan>(queryKey);

      if (previousBScan) {
        const nextBScan: BScan = {
          ...previousBScan,
          ...pathologyUpdate,
        };
        const hasAnyPathology =
          nextBScan.cyst === 1 ||
          nextBScan.hard_exudate === 1 ||
          nextBScan.srf === 1 ||
          nextBScan.ped === 1;
        if (hasAnyPathology) {
          nextBScan.healthy = 0;
        }
        const hasAnyMarker =
          nextBScan.cyst === 0 || nextBScan.cyst === 1 ||
          nextBScan.hard_exudate === 0 || nextBScan.hard_exudate === 1 ||
          nextBScan.srf === 0 || nextBScan.srf === 1 ||
          nextBScan.ped === 0 || nextBScan.ped === 1 ||
          nextBScan.healthy === 0 || nextBScan.healthy === 1;
        nextBScan.is_labeled = hasAnyMarker;
        nextBScan.label = nextBScan.healthy === 1
          ? Label.Healthy
          : nextBScan.healthy === 0
            ? Label.Unhealthy
            : Label.Unlabeled;
        queryClient.setQueryData(queryKey, nextBScan);
      }

      return { previousBScan, queryKey };
    },
    onError: (err, _variables, context) => {
      if (context?.previousBScan) {
        queryClient.setQueryData(context.queryKey, context.previousBScan);
      }
      console.error('Failed to update pathology:', err);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKey, data);
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      queryClient.invalidateQueries({ queryKey: ['scan', scanId, 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['globalStats'] });
    },
  });

  const labelAsHealthy = () => {
    updateLabelMutation.mutate({ healthy: 1 });
  };

  const labelAsUnhealthy = () => {
    updateLabelMutation.mutate({ healthy: 0 });
  };

  const clearLabelMutation = useMutation({
    mutationFn: () => {
      if (!bscanId) {
        return Promise.reject(new Error('No B-scan ID'));
      }
      return api.clearLabel(bscanId);
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey });
      const previousBScan = queryClient.getQueryData<BScan>(queryKey);

      if (previousBScan) {
        queryClient.setQueryData(queryKey, {
          ...previousBScan,
          healthy: null,
          cyst: null,
          hard_exudate: null,
          srf: null,
          ped: null,
          label: Label.Unlabeled,
          is_labeled: false,
        });
      }

      return { previousBScan, queryKey };
    },
    onError: (err, _variables, context) => {
      if (context?.previousBScan) {
        queryClient.setQueryData(context.queryKey, context.previousBScan);
      }
      console.error('Failed to clear label:', err);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKey, data);
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      queryClient.invalidateQueries({ queryKey: ['scan', scanId, 'stats'] });
      queryClient.invalidateQueries({ queryKey: ['globalStats'] });
    },
  });

  return {
    labelAsHealthy,
    labelAsUnhealthy,
    clearLabel: () => clearLabelMutation.mutate(),
    updatePathology: (pathologyUpdate: BScanPathologyUpdate) =>
      updatePathologyMutation.mutate(pathologyUpdate),
    isLoading:
      updateLabelMutation.isPending ||
      updatePathologyMutation.isPending ||
      clearLabelMutation.isPending,
    error: updateLabelMutation.error ?? updatePathologyMutation.error ?? clearLabelMutation.error,
  };
}
