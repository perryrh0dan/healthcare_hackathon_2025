import { useQuery, type UseQueryOptions, type UseQueryResult } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';

function useAuthedQuery<
  TQueryFnData = unknown,
  TError = unknown,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[]
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>
): UseQueryResult<TData, TError> {
  const navigate = useNavigate()

  const query = useQuery(options);

  const error = query.error as any;
  const status = error?.response?.status;

  if (status === 401) {
    navigate({ to: "/login" })
  }

  return query;
}

export default useAuthedQuery;

