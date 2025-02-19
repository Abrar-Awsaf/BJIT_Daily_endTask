/** @odoo-module */
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RfpDashboard extends Component {
    static template = "procurement_management.rfp_dashboard_template";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            selectedSupplier: "",
            selectedDateRange: "this_week",
            startDate: "",
            endDate: "",
            suppliers: [],
            totalRFQs: 0,
            totalAmount: 0,
            keyMetrics: {
                totalApprovedRFQs: 0,
                totalAmount: 0,
                products: [],
            },
        });

        this.fetchSuppliers();

        // ✅ Ensure renderCharts is bound to the current context
        this.renderCharts = this.renderCharts.bind(this);

        // Ensure event handlers are defined
        this.onSupplierChange = this.onSupplierChange.bind(this);
        this.onDateRangeChange = this.onDateRangeChange.bind(this);
        this.onCustomDateChange = this.onCustomDateChange.bind(this);

        onMounted(() => {
            this.fetchDashboardData();
        });
    }

    // Event Handlers
    onSupplierChange(event) {
        this.state.selectedSupplier = event.target.value;
        this.fetchDashboardData();
    }

    onDateRangeChange(event) {
        this.state.selectedDateRange = event.target.value;
        if (this.state.selectedDateRange !== "custom_range") {
            this.state.startDate = "";
            this.state.endDate = "";
        }
        this.fetchDashboardData();
    }

    onCustomDateChange() {
        if (this.state.startDate && this.state.endDate) {
            this.fetchDashboardData();
        }
    }

    async fetchSuppliers() {
        try {
            const supplierRecords = await this.orm.searchRead(
                "res.partner",
                [["supplier_rank", ">", 0]],
                ["id", "name"]
            );

            this.state.suppliers = supplierRecords.map(supplier => ({
                id: supplier.id,
                name: supplier.name
            }));
        } catch (error) {
            console.error("Error fetching suppliers:", error);
        }
    }

    async fetchDashboardData() {
        if (!this.state.selectedSupplier) {
            return;
        }

        try {
            let domain = [["approved_supplier_id", "=", parseInt(this.state.selectedSupplier)]];
            const today = new Date();
            let startDate, endDate;

            if (this.state.selectedDateRange === "this_week") {
                startDate = new Date(today.setDate(today.getDate() - today.getDay()));
                endDate = new Date();
            } else if (this.state.selectedDateRange === "last_week") {
                startDate = new Date(today.setDate(today.getDate() - today.getDay() - 7));
                endDate = new Date(today.setDate(startDate.getDate() + 6));
            } else if (this.state.selectedDateRange === "last_month") {
                startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                endDate = new Date(today.getFullYear(), today.getMonth(), 0);
            } else if (this.state.selectedDateRange === "last_year") {
                startDate = new Date(today.getFullYear() - 1, 0, 1);
                endDate = new Date(today.getFullYear() - 1, 11, 31);
            } else if (this.state.selectedDateRange === "custom_range") {
                startDate = this.state.startDate ? new Date(this.state.startDate) : null;
                endDate = this.state.endDate ? new Date(this.state.endDate) : null;
            }

            if (startDate && endDate) {
                domain.push(["create_date", ">=", startDate.toISOString().split("T")[0]]);
                domain.push(["create_date", "<=", endDate.toISOString().split("T")[0]]);
            }

            const approvedRFQs = await this.orm.searchRead("rfp.management", domain, ["id", "total_amount", "product_line_ids"]);

            let totalAmount = approvedRFQs.reduce((sum, rfp) => sum + rfp.total_amount, 0);
            let totalRFQs = approvedRFQs.length;
            let productCounts = {};
            for (const rfp of approvedRFQs) {
                const rfpLines = await this.orm.searchRead("rfp.product.line", [["rfp_id", "in", approvedRFQs.map(rfp => rfp.id)]], ["product_id", "quantity"]);

                for (const line of rfpLines) {
                    const productName = line.product_id ? line.product_id[1] : "Unknown Product";
                    productCounts[productName] = (productCounts[productName] || 0) + line.quantity;
                }
            }

            this.state.totalRFQs = totalRFQs;
            this.state.totalAmount = totalAmount;
            this.state.keyMetrics.totalApprovedRFQs = totalRFQs;
            this.state.keyMetrics.totalAmount = totalAmount;
            this.state.keyMetrics.products = Object.entries(productCounts).map(([name, quantity]) => ({ name, quantity }));
            console.log("Products data:", this.state.keyMetrics.products);

            this.renderCharts(); // Ensure charts are rendered once data is fetched
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    }

    renderCharts() {
        setTimeout(() => {
            const ctxBar = document.getElementById("rfqBarChart");
            const ctxPie = document.getElementById("rfqPieChart");
            const ctxLine = document.getElementById("rfqLineChart");

            // Destroy previous charts if they exist
            if (ctxBar && ctxBar.chart) ctxBar.chart.destroy();
            if (ctxPie && ctxPie.chart) ctxPie.chart.destroy();
            if (ctxLine && ctxLine.chart) ctxLine.chart.destroy();

            // Create new Bar Chart
            if (ctxBar) {
                const barChart = new Chart(ctxBar, {
                    type: "bar",
                    data: {
                        labels: this.state.keyMetrics.products.map(p => p.name),
                        datasets: [{
                            label: "RFQ Quantities",
                            data: this.state.keyMetrics.products.map(p => p.quantity),
                            backgroundColor: "rgba(54, 162, 235, 0.6)",
                        }],
                    },
                });
                ctxBar.chart = barChart;  // Store the chart instance
            }

            // Create new Pie Chart
            if (ctxPie) {
                const pieChart = new Chart(ctxPie, {
                    type: "pie",
                    data: {
                        labels: this.state.keyMetrics.products.map(p => p.name),
                        datasets: [{
                            data: this.state.keyMetrics.products.map(p => p.quantity),
                            backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"],
                        }],
                    },
                });
                ctxPie.chart = pieChart;  // Store the chart instance
            }

            // Create new Line Chart
            if (ctxLine) {
                const lineChart = new Chart(ctxLine, {
                    type: "line",
                    data: {
                        labels: this.state.keyMetrics.products.map(p => p.name),
                        datasets: [{
                            label: "RFQ Trends",
                            data: this.state.keyMetrics.products.map(p => p.quantity),
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            borderColor: "rgba(75, 192, 192, 1)",
                            borderWidth: 1,
                        }],
                    },
                });
                ctxLine.chart = lineChart;  // Store the chart instance
            }
        }, 500);
    }
}

// ✅ Register the OWL Component Properly in the Registry
registry.category("actions").add("rfp_dashboard", RfpDashboard);
export default RfpDashboard;
