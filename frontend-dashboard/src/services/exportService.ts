import api from "./api";

export const exportCSV = async () => {
  try {
    const response = await api.get("/verdicts/export/csv", {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "verdicts.csv");

    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("CSV Export Failed", error);
  }
};

export const exportPDF = async () => {
  try {
    const response = await api.get("/verdicts/export/pdf", {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "verdicts.pdf");

    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("PDF Export Failed", error);
  }
};