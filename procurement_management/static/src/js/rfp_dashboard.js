/** @odoo-module */
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RfpDashboard extends Component {
    static template = "procurement_management.rfp_dashboard_template";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            selectedSupplier: "",
            selectedDateRange: "this_week", // Default date range
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

            console.log("Fetching RFQs with domain:", domain);

            const approvedRFQs = await this.orm.searchRead(
                "rfp.management",
                domain,
                ["id", "total_amount", "product_line_ids"]
            );

            console.log("Fetched RFQs:", approvedRFQs);

            let totalAmount = approvedRFQs.reduce((sum, rfp) => sum + rfp.total_amount, 0);
            let totalRFQs = approvedRFQs.length;
            let productCounts = {};
            for (const rfp of approvedRFQs) {
                const rfpLines = await this.orm.searchRead(
                    "rfp.product.line",
                    [["rfp_id", "in", approvedRFQs.map(rfp => rfp.id)]],
                    ["product_id", "quantity"]
                );

                for (const line of rfpLines) {
                    const productName = line.product_id[1];
                    productCounts[productName] = (productCounts[productName] || 0) + line.quantity;
                }
            }

            console.log("Approved RFQs:", approvedRFQs);
            console.log("Fetching Product Lines for:", approvedRFQs.map(rfp => rfp.product_line_ids));

            console.log("Product Breakdown:", productCounts);

            this.state.totalRFQs = totalRFQs;
            this.state.totalAmount = totalAmount;
            this.state.keyMetrics.totalApprovedRFQs = totalRFQs;
            this.state.keyMetrics.totalAmount = totalAmount;
            this.state.keyMetrics.products = Object.entries(productCounts).map(([name, quantity]) => ({
                name,
                quantity
            }));
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    }

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
}
// ✅ Register the OWL Component Properly in the Registry
registry.category("actions").add("rfp_dashboard", RfpDashboard);
export default RfpDashboard;