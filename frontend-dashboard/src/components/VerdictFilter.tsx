interface VerdictFilterProps {
  selectedStatus: string;
  onStatusChange: (status: string) => void;
}

function VerdictFilter({
  selectedStatus,
  onStatusChange,
}: VerdictFilterProps) {
  return (
    <div className="verdict-filter">
      <label htmlFor="verdict-status-filter">
        Filter by Status:
      </label>

      <select
        id="verdict-status-filter"
        value={selectedStatus}
        onChange={(e) => onStatusChange(e.target.value)}
      >
        <option value="All">All</option>
        <option value="Detected">Detected</option>
        <option value="Missed">Missed</option>
        <option value="Partial">Partial</option>
        <option value="No Data">No Data</option>
      </select>
    </div>
  );
}

export default VerdictFilter;