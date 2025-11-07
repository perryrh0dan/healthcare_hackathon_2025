import { useMutation, type UseMutationOptions, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';

function useAuthedMutation<
  TData = unknown,
  TError = unknown,
  TVariables = void,
  TContext = unknown
>(
  options: UseMutationOptions<TData, TError, TVariables, TContext>
): UseMutationResult<TData, TError, TVariables, TContext> {
  const navigate = useNavigate()

  const mutation = useMutation({
    ...options,
    onError: (error, variables, onMutateResult, context) => {
      const status = (error as any)?.response?.status;

      if (status === 401) {
        navigate({ to: "/login" })
        return;
      }

      options.onError?.(error, variables, onMutateResult, context);
    },
  });

  return mutation;
}

export default useAuthedMutation;

