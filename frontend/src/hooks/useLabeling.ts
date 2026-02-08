/**
 * Labeling hook for updating B-scan labels with optimistic UI.
 * Handles label mutations and auto-advance after success.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Label, type BScan } from '@/types';

interface UseLabelingProps {
  scanId: string;
  bscanId: number | undefined;
  onSuccess?: () => void;
}

/**
 * Hook for managing label updates with optimistic UI.
 */
export function useLabeling({ scanId, bscanId, onSuccess }: UseLabelingProps) {
  const queryClient = useQueryClient();

  const updateLabelMutation = useMutation({
    mutationFn: ({ label }: { label: Label.Healthy | Label.Unhealthy }) => {
      if (!bscanId) {
        return Promise.reject(new Error('No B-scan ID'));
      }
      return api.updateLabel(bscanId, { label });
    },
    onMutate: async ({ label }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: ['bscan', scanId],
      });

      // Snapshot previous value
      const previousBScan = queryClient.getQueryData<BScan>(['bscan', scanId, bscanId]);

      // Optimistically update
      if (previousBScan) {
        queryClient.setQueryData(['bscan', scanId, bscanId], {
          ...previousBScan,
          label,
        });
      }

      return { previousBScan };
    },
    onError: (err, variables, context) => {
      // Revert on error
      if (context?.previousBScan) {
        queryClient.setQueryData(
          ['bscan', scanId, bscanId],
          context.previousBScan
        );
      }
      console.error('Failed to update label:', err);
    },
    onSuccess: (data) => {
      // Update cache with server response
      queryClient.setQueryData(['bscan', scanId, data.id], data);

      // Invalidate scans list to refresh statistics
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      queryClient.invalidateQueries({ queryKey: ['scan', scanId, 'stats'] });

      // Call auto-advance callback
      if (onSuccess) {
        onSuccess();
      }
    },
  });

  const labelAsHealthy = () => {
    updateLabelMutation.mutate({ label: Label.Healthy });
  };

  const labelAsUnhealthy = () => {
    updateLabelMutation.mutate({ label: Label.Unhealthy });
  };

  return {
    labelAsHealthy,
    labelAsUnhealthy,
    isLoading: updateLabelMutation.isPending,
    error: updateLabelMutation.error,
  };
}
