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
        {/*
          M2: the `value` is the token sent to the API, so it has to be the
          canonical `NoData` that Delta emits and that its frozen schema
          declares -- `validate_rule` normalizes the legacy `"No Data"`
          spelling on input, but a filter built on the old spelling never
          matched a stored row. The label stays spaced for readability.
        */}
        <option value="NoData">No Data</option>
      </select>
    </div>
  );
}

export default VerdictFilter;