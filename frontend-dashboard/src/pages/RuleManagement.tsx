import { useEffect, useState } from "react";
import RuleComparison from "../components/rules/RuleComparison";

import {
  searchRules,
  createRule,
  updateRule,
  deleteRule,
  submitRule,
  approveRule,
  rejectRule,
} from "../services/ruleService";

import type {
  Rule,
  RuleInput,
} from "../services/ruleService";

const emptyRule: RuleInput = {
  rule_name: "",
  rule_type: "Sigma",
  severity: "Medium",
  description: "",
  query: "",
  status: "Draft",
  mitre_technique: "",
};

export default function RuleManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [search, setSearch] = useState("");

  const [selectedRuleId, setSelectedRuleId] =
    useState<number | null>(null);

  const [editingRule, setEditingRule] =
    useState<Rule | null>(null);

  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] =
    useState<RuleInput>(emptyRule);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionLoading, setActionLoading] =
    useState<number | null>(null);

  const [error, setError] = useState("");

  // --------------------------------------------------
  // Load rules
  // --------------------------------------------------

  const fetchRules = async (query = search) => {
    try {
      setLoading(true);
      setError("");

      const data = await searchRules(query);

      setRules(data);
    } catch (err: any) {
      console.error("Failed to fetch rules:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load rules."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules("");
  }, []);

  // --------------------------------------------------
  // Search
  // --------------------------------------------------

  const handleSearch = async () => {
    await fetchRules(search);
  };

  const handleClearSearch = async () => {
    setSearch("");
    await fetchRules("");
  };

  // --------------------------------------------------
  // Create / Edit
  // --------------------------------------------------

  const openCreateForm = () => {
    setEditingRule(null);

    setFormData({
      ...emptyRule,
    });

    setShowForm(true);
    setError("");
  };

  const openEditForm = (rule: Rule) => {
    setEditingRule(rule);

    setFormData({
      rule_name: rule.rule_name,
      rule_type: rule.rule_type,
      severity: rule.severity,
      description: rule.description || "",
      query: rule.query,
      status: rule.status,
      mitre_technique:
        rule.mitre_technique || "",
    });

    setShowForm(true);
    setError("");
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingRule(null);

    setFormData({
      ...emptyRule,
    });
  };

  const handleInputChange = (
    field: keyof RuleInput,
    value: string
  ) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSaveRule = async (
    event: React.FormEvent
  ) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      if (editingRule) {
        await updateRule(
          editingRule.id,
          formData
        );
      } else {
        await createRule(formData);
      }

      closeForm();

      await fetchRules(search);
    } catch (err: any) {
      console.error("Failed to save rule:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to save rule."
      );
    } finally {
      setSaving(false);
    }
  };

  // --------------------------------------------------
  // Delete
  // --------------------------------------------------

  const handleDelete = async (rule: Rule) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${rule.rule_name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setActionLoading(rule.id);

      await deleteRule(rule.id);

      if (selectedRuleId === rule.id) {
        setSelectedRuleId(null);
      }

      await fetchRules(search);
    } catch (err: any) {
      console.error("Failed to delete rule:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to delete rule."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // --------------------------------------------------
  // Submit for approval
  // --------------------------------------------------

  const handleSubmitForApproval = async (
    rule: Rule
  ) => {
    try {
      setError("");
      setActionLoading(rule.id);

      await submitRule(rule.id);

      await fetchRules(search);
    } catch (err: any) {
      console.error(
        "Failed to submit rule:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to submit rule for approval."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // --------------------------------------------------
  // Approve
  // --------------------------------------------------

  const handleApprove = async (rule: Rule) => {
    try {
      setError("");
      setActionLoading(rule.id);

      await approveRule(rule.id);

      await fetchRules(search);
    } catch (err: any) {
      console.error(
        "Failed to approve rule:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to approve rule."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // --------------------------------------------------
  // Reject
  // --------------------------------------------------

  const handleReject = async (rule: Rule) => {
    const confirmed = window.confirm(
      `Reject "${rule.rule_name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setActionLoading(rule.id);

      await rejectRule(rule.id);

      await fetchRules(search);
    } catch (err: any) {
      console.error(
        "Failed to reject rule:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to reject rule."
      );
    } finally {
      setActionLoading(null);
    }
  };

  // --------------------------------------------------
  // Styling
  // --------------------------------------------------

  const getSeverityClass = (
    severity: string
  ) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "bg-red-100 text-red-700";

      case "high":
        return "bg-orange-100 text-orange-700";

      case "medium":
        return "bg-yellow-100 text-yellow-700";

      case "low":
        return "bg-green-100 text-green-700";

      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getStatusClass = (
    status: string
  ) => {
    switch (status.toLowerCase()) {
      case "approved":
        return "bg-green-100 text-green-700";

      case "pending":
        return "bg-yellow-100 text-yellow-700";

      case "draft":
        return "bg-gray-100 text-gray-700";

      case "rejected":
        return "bg-red-100 text-red-700";

      default:
        return "bg-blue-100 text-blue-700";
    }
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="p-6">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">

        <div>
          <h2 className="text-2xl font-bold">
            Rule Management
          </h2>

          <p className="text-gray-500 mt-1">
            Manage, review, and approve detection rules.
          </p>
        </div>

        <button
          onClick={openCreateForm}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          + Create Rule
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 text-red-700 border border-red-300 rounded p-3 mb-5">
          {error}
        </div>
      )}

      {/* Search */}
      <div className="bg-white border rounded-lg p-4 mb-6">

        <div className="flex flex-col md:flex-row gap-3">

          <input
            type="text"
            placeholder="Search rules..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSearch();
              }
            }}
            className="border rounded p-2 flex-1"
          />

          <button
            onClick={handleSearch}
            className="bg-gray-800 hover:bg-gray-900 text-white px-5 py-2 rounded"
          >
            Search
          </button>

          <button
            onClick={handleClearSearch}
            className="border px-5 py-2 rounded hover:bg-gray-50"
          >
            Clear
          </button>

        </div>
      </div>

      {/* Rules table */}
      <div className="bg-white border rounded-lg overflow-hidden">

        <div className="overflow-x-auto">

          <table className="w-full">

            <thead className="bg-gray-100">

              <tr>

                <th className="text-left p-3 border-b">
                  Rule
                </th>

                <th className="text-left p-3 border-b">
                  Type
                </th>

                <th className="text-left p-3 border-b">
                  Severity
                </th>

                <th className="text-left p-3 border-b">
                  Status
                </th>

                <th className="text-left p-3 border-b">
                  MITRE
                </th>

                <th className="text-left p-3 border-b">
                  Actions
                </th>

              </tr>

            </thead>

            <tbody>

              {loading ? (

                <tr>
                  <td
                    colSpan={6}
                    className="text-center p-6 text-gray-500"
                  >
                    Loading rules...
                  </td>
                </tr>

              ) : rules.length === 0 ? (

                <tr>
                  <td
                    colSpan={6}
                    className="text-center p-6 text-gray-500"
                  >
                    No rules found.
                  </td>
                </tr>

              ) : (

                rules.map((rule) => {

                  const busy =
                    actionLoading === rule.id;

                  return (
                    <tr
                      key={rule.id}
                      className="hover:bg-gray-50"
                    >

                      <td className="p-3 border-b font-medium">
                        {rule.rule_name}
                      </td>

                      <td className="p-3 border-b">
                        {rule.rule_type}
                      </td>

                      <td className="p-3 border-b">

                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${getSeverityClass(
                            rule.severity
                          )}`}
                        >
                          {rule.severity}
                        </span>

                      </td>

                      <td className="p-3 border-b">

                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${getStatusClass(
                            rule.status
                          )}`}
                        >
                          {rule.status}
                        </span>

                      </td>

                      <td className="p-3 border-b">
                        {rule.mitre_technique || "-"}
                      </td>

                      <td className="p-3 border-b">

                        <div className="flex flex-wrap gap-2">

                          {/* Compare */}
                          <button
                            disabled={busy}
                            onClick={() =>
                              setSelectedRuleId(rule.id)
                            }
                            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                          >
                            Compare
                          </button>

                          {/* Edit */}
                          <button
                            disabled={busy}
                            onClick={() =>
                              openEditForm(rule)
                            }
                            className="bg-gray-700 hover:bg-gray-800 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                          >
                            Edit
                          </button>

                          {/* Draft -> Pending */}
                          {rule.status === "Draft" && (
                            <button
                              disabled={busy}
                              onClick={() =>
                                handleSubmitForApproval(rule)
                              }
                              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                            >
                              {busy
                                ? "Processing..."
                                : "Submit"}
                            </button>
                          )}

                          {/* Pending -> Approved / Rejected */}
                          {rule.status === "Pending" && (
                            <>
                              <button
                                disabled={busy}
                                onClick={() =>
                                  handleApprove(rule)
                                }
                                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                              >
                                {busy
                                  ? "Processing..."
                                  : "Approve"}
                              </button>

                              <button
                                disabled={busy}
                                onClick={() =>
                                  handleReject(rule)
                                }
                                className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                              >
                                {busy
                                  ? "Processing..."
                                  : "Reject"}
                              </button>
                            </>
                          )}

                          {/* Rejected -> Pending */}
                          {rule.status === "Rejected" && (
                            <button
                              disabled={busy}
                              onClick={() =>
                                handleSubmitForApproval(rule)
                              }
                              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                            >
                              {busy
                                ? "Processing..."
                                : "Resubmit"}
                            </button>
                          )}

                          {/* Delete */}
                          <button
                            disabled={busy}
                            onClick={() =>
                              handleDelete(rule)
                            }
                            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
                          >
                            Delete
                          </button>

                        </div>

                      </td>

                    </tr>
                  );
                })

              )}

            </tbody>

          </table>

        </div>
      </div>

      {/* Comparison */}
      {selectedRuleId !== null && (

        <div className="mt-6">

          <div className="flex justify-end mb-2">

            <button
              onClick={() =>
                setSelectedRuleId(null)
              }
              className="text-gray-600 hover:text-gray-900"
            >
              Close comparison
            </button>

          </div>

          <RuleComparison
            ruleId={selectedRuleId}
          />

        </div>

      )}

      {/* Create/Edit modal */}
      {showForm && (

        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">

          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">

            {/* Modal header */}
            <div className="flex items-center justify-between p-5 border-b">

              <h3 className="text-xl font-bold">

                {editingRule
                  ? "Edit Rule"
                  : "Create Rule"}

              </h3>

              <button
                onClick={closeForm}
                className="text-gray-500 hover:text-gray-900 text-xl"
              >
                ×
              </button>

            </div>

            {/* Form */}
            <form
              onSubmit={handleSaveRule}
              className="p-5 space-y-4"
            >

              {/* Rule name */}
              <div>

                <label className="block text-sm font-medium mb-1">
                  Rule Name
                </label>

                <input
                  required
                  value={formData.rule_name}
                  onChange={(event) =>
                    handleInputChange(
                      "rule_name",
                      event.target.value
                    )
                  }
                  className="border rounded p-2 w-full"
                />

              </div>

              {/* Type / Severity */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                <div>

                  <label className="block text-sm font-medium mb-1">
                    Rule Type
                  </label>

                  <select
                    value={formData.rule_type}
                    onChange={(event) =>
                      handleInputChange(
                        "rule_type",
                        event.target.value
                      )
                    }
                    className="border rounded p-2 w-full"
                  >

                    <option value="Sigma">
                      Sigma
                    </option>

                    <option value="KQL">
                      KQL
                    </option>

                    <option value="SPL">
                      SPL
                    </option>

                    <option value="EQL">
                      EQL
                    </option>

                  </select>

                </div>

                <div>

                  <label className="block text-sm font-medium mb-1">
                    Severity
                  </label>

                  <select
                    value={formData.severity}
                    onChange={(event) =>
                      handleInputChange(
                        "severity",
                        event.target.value
                      )
                    }
                    className="border rounded p-2 w-full"
                  >

                    <option value="Low">
                      Low
                    </option>

                    <option value="Medium">
                      Medium
                    </option>

                    <option value="High">
                      High
                    </option>

                    <option value="Critical">
                      Critical
                    </option>

                  </select>

                </div>

              </div>

              {/* MITRE */}
              <div>

                <label className="block text-sm font-medium mb-1">
                  MITRE Technique
                </label>

                <input
                  value={
                    formData.mitre_technique || ""
                  }
                  onChange={(event) =>
                    handleInputChange(
                      "mitre_technique",
                      event.target.value
                    )
                  }
                  placeholder="Example: T1059.001"
                  className="border rounded p-2 w-full"
                />

              </div>

              {/* Status */}
              <div>

                <label className="block text-sm font-medium mb-1">
                  Status
                </label>

                <select
                  value={formData.status}
                  onChange={(event) =>
                    handleInputChange(
                      "status",
                      event.target.value
                    )
                  }
                  className="border rounded p-2 w-full"
                >

                  <option value="Draft">
                    Draft
                  </option>

                  <option value="Pending">
                    Pending
                  </option>

                  <option value="Approved">
                    Approved
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>

                </select>

              </div>

              {/* Description */}
              <div>

                <label className="block text-sm font-medium mb-1">
                  Description
                </label>

                <textarea
                  value={
                    formData.description || ""
                  }
                  onChange={(event) =>
                    handleInputChange(
                      "description",
                      event.target.value
                    )
                  }
                  rows={3}
                  className="border rounded p-2 w-full"
                />

              </div>

              {/* Query */}
              <div>

                <label className="block text-sm font-medium mb-1">
                  Query
                </label>

                <textarea
                  required
                  value={formData.query}
                  onChange={(event) =>
                    handleInputChange(
                      "query",
                      event.target.value
                    )
                  }
                  rows={6}
                  placeholder="Enter detection query..."
                  className="border rounded p-2 w-full font-mono text-sm"
                />

              </div>

              {/* Form buttons */}
              <div className="flex justify-end gap-3 pt-3 border-t">

                <button
                  type="button"
                  onClick={closeForm}
                  className="border px-4 py-2 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-5 py-2 rounded"
                >
                  {saving
                    ? "Saving..."
                    : editingRule
                    ? "Update Rule"
                    : "Create Rule"}
                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>
  );
}
