/**
 * Scan list page - sortable table of all scans with progress.
 */

import { Fragment, useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import ProgressBar from '@/components/ProgressBar';
import styles from './ScanListPage.module.css';

type SortKey =
  | 'scan_id'
  | 'labeled'
  | 'healthy'
  | 'unhealthy'
  | 'not_necessary_healthy'
  | 'cyst_positive'
  | 'hard_exudate_positive'
  | 'srf_positive'
  | 'ped_positive'
  | 'percent_complete';
type SortDir = 'asc' | 'desc';
type ToggleColumnKey =
  | 'scan_id'
  | 'labeled'
  | 'healthy'
  | 'unhealthy'
  | 'not_necessary_healthy'
  | 'cyst_positive'
  | 'hard_exudate_positive'
  | 'srf_positive'
  | 'ped_positive';

type ColumnConfig = {
  key: ToggleColumnKey;
  label: string;
  sortKey: SortKey;
  className?: string;
  isNumeric?: boolean;
};

const COLUMN_CONFIG: ColumnConfig[] = [
  { key: 'scan_id', label: 'Scan ID', sortKey: 'scan_id' },
  { key: 'labeled', label: 'Labeled', sortKey: 'labeled', isNumeric: true },
  { key: 'healthy', label: 'Healthy', sortKey: 'healthy', className: 'healthy', isNumeric: true },
  { key: 'unhealthy', label: 'Not Healthy', sortKey: 'unhealthy', className: 'unhealthy', isNumeric: true },
  { key: 'not_necessary_healthy', label: 'Not Necessarily Healthy', sortKey: 'not_necessary_healthy', isNumeric: true },
  { key: 'cyst_positive', label: 'Cyst', sortKey: 'cyst_positive', isNumeric: true },
  { key: 'hard_exudate_positive', label: 'Hard Exudate', sortKey: 'hard_exudate_positive', isNumeric: true },
  { key: 'srf_positive', label: 'SRF', sortKey: 'srf_positive', isNumeric: true },
  { key: 'ped_positive', label: 'PED', sortKey: 'ped_positive', isNumeric: true },
];

const DEFAULT_VISIBLE_COLUMNS: Record<ToggleColumnKey, boolean> = {
  scan_id: true,
  labeled: true,
  healthy: false,
  unhealthy: true,
  not_necessary_healthy: false,
  cyst_positive: true,
  hard_exudate_positive: true,
  srf_positive: true,
  ped_positive: true,
};

function markerValue(value: number | null): string {
  if (value === 1) return '1';
  if (value === 0) return '0';
  return '—';
}

function markerClass(value: number | null): string {
  if (value === null) return '';
  return value >= 1 ? styles.markerPositive : '';
}

function healthState(healthy: number | null, isLabeled: boolean): string {
  if (healthy === 1) return 'Healthy';
  if (healthy === 0) return 'Not healthy';
  if (isLabeled) return 'Not necessarily healthy';
  return 'Unlabeled';
}

function ScanBScansTable({ scanId }: { scanId: string }) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['scanBScans', scanId],
    queryFn: () => api.getScanBScans(scanId),
  });

  if (isLoading) {
    return <p className={styles.detailsLoading}>Loading B-scans…</p>;
  }

  if (isError) {
    return (
      <p className={styles.detailsError}>
        Failed to load B-scans: {error instanceof Error ? error.message : 'Unknown error'}
      </p>
    );
  }

  if (!data || data.length === 0) {
    return <p className={styles.detailsLoading}>No B-scans found.</p>;
  }

  return (
    <div className={styles.bscanTableWrap}>
      <table className={styles.bscanTable}>
        <thead>
          <tr>
            <th>Index</th>
            <th>Health</th>
            <th>Cyst</th>
            <th>Hard exudate</th>
            <th>SRF</th>
            <th>PED</th>
            <th>Labeled</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id}>
              <td>{item.bscan_index}</td>
              <td>{healthState(item.healthy, item.is_labeled)}</td>
              <td className={markerClass(item.cyst)}>{markerValue(item.cyst)}</td>
              <td className={markerClass(item.hard_exudate)}>{markerValue(item.hard_exudate)}</td>
              <td className={markerClass(item.srf)}>{markerValue(item.srf)}</td>
              <td className={markerClass(item.ped)}>{markerValue(item.ped)}</td>
              <td>{item.is_labeled ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScanListPage() {
  const [sortKey, setSortKey] = useState<SortKey>('scan_id');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [isExporting, setIsExporting] = useState(false);
  const [visibleColumns, setVisibleColumns] = useState<Record<ToggleColumnKey, boolean>>(
    DEFAULT_VISIBLE_COLUMNS
  );

  const {
    data: scans,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['scans'],
    queryFn: api.getScans,
  });

  const { data: globalStats } = useQuery({
    queryKey: ['globalStats'],
    queryFn: api.getGlobalStats,
  });

  const visibleColumnConfigs = useMemo(
    () => COLUMN_CONFIG.filter((col) => visibleColumns[col.key]),
    [visibleColumns]
  );

  const sortedScans = useMemo(() => {
    if (!scans) return [];
    return [...scans].sort((a, b) => {
      let va: number | string;
      let vb: number | string;
      switch (sortKey) {
        case 'scan_id':
          va = a.scan_id; vb = b.scan_id; break;
        case 'labeled':
          va = a.stats.labeled; vb = b.stats.labeled; break;
        case 'healthy':
          va = a.stats.healthy; vb = b.stats.healthy; break;
        case 'unhealthy':
          va = a.stats.unhealthy; vb = b.stats.unhealthy; break;
        case 'not_necessary_healthy':
          va = a.stats.not_necessary_healthy; vb = b.stats.not_necessary_healthy; break;
        case 'cyst_positive':
          va = a.stats.cyst_positive; vb = b.stats.cyst_positive; break;
        case 'hard_exudate_positive':
          va = a.stats.hard_exudate_positive; vb = b.stats.hard_exudate_positive; break;
        case 'srf_positive':
          va = a.stats.srf_positive; vb = b.stats.srf_positive; break;
        case 'ped_positive':
          va = a.stats.ped_positive; vb = b.stats.ped_positive; break;
        case 'percent_complete':
          va = a.stats.percent_complete; vb = b.stats.percent_complete; break;
        default:
          va = a.scan_id; vb = b.scan_id;
      }
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [scans, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sortIndicator = (key: SortKey) => {
    if (sortKey !== key) return '';
    return sortDir === 'asc' ? ' ▲' : ' ▼';
  };

  const toggleExpanded = (scanId: string) => {
    setExpanded((prev) => ({ ...prev, [scanId]: !prev[scanId] }));
  };

  const toggleColumn = (column: ToggleColumnKey) => {
    setVisibleColumns((prev) => {
      const next = { ...prev, [column]: !prev[column] };
      const visibleCount = Object.values(next).filter(Boolean).length;
      if (visibleCount === 0) {
        return prev;
      }
      return next;
    });
  };

  const handleExportCsv = async () => {
    try {
      setIsExporting(true);
      const blob = await api.downloadBScansCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'bscans_export.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
  };

  const renderDataCell = (
    scan: (typeof sortedScans)[number],
    column: ColumnConfig
  ) => {
    switch (column.key) {
      case 'scan_id':
        return (
          <td key={column.key}>
            <Link to={`/scan/${scan.scan_id}`} className={styles.scanLink}>
              {scan.scan_id}
            </Link>
          </td>
        );
      case 'labeled':
        return (
          <td key={column.key} className={styles.numCol}>
            {scan.stats.labeled} / {scan.stats.total_bscans}
          </td>
        );
      case 'healthy':
        return <td key={column.key} className={`${styles.numCol} ${styles.healthy}`}>{scan.stats.healthy}</td>;
      case 'unhealthy':
        return <td key={column.key} className={`${styles.numCol} ${styles.unhealthy}`}>{scan.stats.unhealthy}</td>;
      case 'not_necessary_healthy':
        return <td key={column.key} className={styles.numCol}>{scan.stats.not_necessary_healthy}</td>;
      case 'cyst_positive':
        return (
          <td
            key={column.key}
            className={`${styles.numCol} ${scan.stats.cyst_positive > 0 ? styles.markerPositive : ''}`}
          >
            {scan.stats.cyst_positive}
          </td>
        );
      case 'hard_exudate_positive':
        return (
          <td
            key={column.key}
            className={`${styles.numCol} ${scan.stats.hard_exudate_positive > 0 ? styles.markerPositive : ''}`}
          >
            {scan.stats.hard_exudate_positive}
          </td>
        );
      case 'srf_positive':
        return (
          <td
            key={column.key}
            className={`${styles.numCol} ${scan.stats.srf_positive > 0 ? styles.markerPositive : ''}`}
          >
            {scan.stats.srf_positive}
          </td>
        );
      case 'ped_positive':
        return (
          <td
            key={column.key}
            className={`${styles.numCol} ${scan.stats.ped_positive > 0 ? styles.markerPositive : ''}`}
          >
            {scan.stats.ped_positive}
          </td>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="container">
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading scans...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container">
        <div className={styles.error}>
          <h2>Error Loading Scans</h2>
          <p>{error instanceof Error ? error.message : 'Unknown error occurred'}</p>
          <button
            className={styles.retryButton}
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!scans || scans.length === 0) {
    return (
      <div className="container">
        <div className={styles.empty}>
          <h2>No Scans Found</h2>
          <p>Import OCT scans using the CLI tool to get started.</p>
          <pre className={styles.code}>
            python scripts/import_scan.py --scan-id SCAN_001 --source /path/to/scans/
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      {globalStats && (
        <div className={styles.statsBar}>
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_scans}</span>
            <span className={styles.statLbl}>Scans</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_bscans}</span>
            <span className={styles.statLbl}>B-scans</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_labeled}</span>
            <span className={styles.statLbl}>Labeled</span>
          </div>
          <div className={styles.statDivider} />
          <div className={`${styles.statItem} ${styles.healthyStat}`}>
            <span className={styles.statNum}>{globalStats.total_healthy}</span>
            <span className={styles.statLbl}>Healthy</span>
          </div>
          <div className={styles.statDivider} />
          <div className={`${styles.statItem} ${styles.unhealthyStat}`}>
            <span className={styles.statNum}>{globalStats.total_unhealthy}</span>
            <span className={styles.statLbl}>Not healthy</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statNum}>{globalStats.total_not_necessary_healthy}</span>
            <span className={styles.statLbl}>Not necessarily healthy</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statProgress}>
            <ProgressBar percentage={globalStats.percent_complete} />
          </div>
        </div>
      )}

      <div className={styles.columnPicker}>
        <div className={styles.columnPickerHeader}>
          <div className={styles.columnPickerTitle}>Visible columns</div>
          <button
            type="button"
            className={styles.exportButton}
            onClick={handleExportCsv}
            disabled={isExporting}
          >
            {isExporting ? 'Exporting…' : 'Export CSV'}
          </button>
        </div>
        <div className={styles.columnPickerGrid}>
          {COLUMN_CONFIG.map((column) => (
            <label key={column.key} className={styles.columnOption}>
              <input
                type="checkbox"
                checked={visibleColumns[column.key]}
                onChange={() => toggleColumn(column.key)}
              />
              <span>{column.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              {visibleColumnConfigs.map((column) => (
                <th
                  key={column.key}
                  className={`${styles.sortable} ${column.isNumeric ? styles.numCol : ''} ${column.className ? styles[column.className] : ''}`}
                  onClick={() => handleSort(column.sortKey)}
                >
                  {column.label}{sortIndicator(column.sortKey)}
                </th>
              ))}
              <th
                className={`${styles.sortable} ${styles.stickyProgressHeader}`}
                onClick={() => handleSort('percent_complete')}
              >
                Progress{sortIndicator('percent_complete')}
              </th>
              <th className={styles.actionsHeader}>Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedScans.map((scan) => {
              const isComplete = scan.stats.percent_complete === 100;
              const isInProgress = scan.stats.labeled > 0 && !isComplete;
              const isExpanded = !!expanded[scan.scan_id];
              const colSpan = visibleColumnConfigs.length + 2;
              return (
                <Fragment key={scan.scan_id}>
                  <tr>
                    {visibleColumnConfigs.map((column) => renderDataCell(scan, column))}
                    <td className={`${styles.progressCol} ${styles.stickyProgressCell}`}>
                      <ProgressBar percentage={scan.stats.percent_complete} showLabel={false} />
                      <span className={styles.pct}>{scan.stats.percent_complete.toFixed(1)}%</span>
                    </td>
                    <td className={styles.actionsCell}>
                      <button
                        className={styles.expandButton}
                        onClick={() => toggleExpanded(scan.scan_id)}
                      >
                        {isExpanded ? 'Hide' : 'Details'}
                      </button>
                      <Link to={`/scan/${scan.scan_id}`} className={styles.actionLink}>
                        {isComplete ? 'Review' : isInProgress ? 'Continue' : 'Start'}
                      </Link>
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className={styles.expandedRow}>
                      <td colSpan={colSpan}>
                        <div className={styles.detailsPanel}>
                          <div className={styles.detailsBlock}>
                            <h4>B-scan Details</h4>
                            <ScanBScansTable scanId={scan.scan_id} />
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ScanListPage;
