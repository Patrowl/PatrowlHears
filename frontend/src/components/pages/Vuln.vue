<template>
    <div>
        <v-tabs
            left
            background-color="white"
            color="deep-orange accent-4"
        >

            <!-- Summary -->
            <v-tab>Summary</v-tab>
            <v-tab>
                <v-badge
                    :color = getNumberColor(this.counter.count_exploit)
                    :content='this.count_exploit'
                >
                    Exploits
                </v-badge>
            </v-tab>
            <v-tab>
                <v-badge
                    :color = getNumberColor(this.counter.count_threat)
                    :content='this.count_threat'
                >
                    Threat activities
                </v-badge>
            </v-tab>
            <v-tab>Comment</v-tab>
            

            <!-- Information Vulnerability --> 
        <v-tab-item>
                <VulnDetails
                    :vuln_id = this.vuln_id
                    @OpenSnackBar = this.modifySnackBar
                />
            </v-tab-item>

            <!-- Exploits --> 
            <v-tab-item>
                <VulnerabilityExploit 
                    :vuln_id = this.vuln_id
                    @OpenSnackBar = this.modifySnackBar
                    @UpdateCounter = this.getCountThreatsExploits
                />
            </v-tab-item>

            <!-- Threat --> 
            <v-tab-item>
                <VulnerabilityThreat 
                    :vuln_id = this.vuln_id
                    @OpenSnackBar = this.modifySnackBar
                    @UpdateCounter = this.getCountThreatsExploits
                />
            </v-tab-item>

            <!-- Comment --> 
            <v-tab-item>
                <VulnerabilityComment
                    :vuln_id = this.vuln_id
                    @OpenSnackBar = this.modifySnackBar
                />
            </v-tab-item>

            
        </v-tabs>
        <SnackBar 
            :snack = snack
        />
    </div>
</template>

<script>
import VulnDetails from "@/components/vulnerability/vulnerabilityDetails/VulnDetails.vue";
import VulnerabilityExploit from "@/components/vulnerability/exploit/VulnerabilityExploit.vue";
import VulnerabilityThreat from "@/components/vulnerability/threat/VulnerabilityThreat.vue";
import VulnerabilityComment from "@/components/vulnerability/comment/VulnerabilityComment.vue";
import Colors from "@/common/colors";
import SnackBar from "@/components/vulnerability/snackBar/SnackBar.vue";
import swal from 'sweetalert2';


export default {
    mixins: [
        Colors,
    ],
    components: {
        VulnDetails,
        VulnerabilityExploit,
        VulnerabilityThreat,
        VulnerabilityComment,
        SnackBar
    },
    data: () => ({
        vuln_id: "",
        snack: {
            open: false,
            color: '',
            text: '',
        },
        counter: {
            count_exploit: 0,
            count_threat: 0,
        }
    }),
    beforeRouteUpdate(to) {
        this.vuln_id = to.params.vuln_id;
    },
    mounted() {
        this.vuln_id = this.$router.currentRoute.params.vuln_id;
        this.getDataFromApi(this.vuln_id)
    },
    computed: {
        count_exploit(){
            return this.counter.count_exploit === 0 ? "0" : this.counter.count_exploit
        },
        count_threat(){
            return this.counter.count_threat === 0 ? "0" : this.counter.count_threat
        }
    },
    methods: {
        modifySnackBar(value) {
            this.snack = value
        },
        getDataFromApi(vuln_id) {
            return new Promise((resolve, reject) => {
                let counter = this.getCountThreatsExploits(vuln_id);

                setTimeout(() => {
                    this.loading = false;
                    resolve({ counter });
                }, 300);
            });
        },
        getCountThreatsExploits(vuln_id) {
            this.loading = true;
            this.$api.get('/api/vulns/'+vuln_id+'/counter').then(res => {
                if (res && res.status === 200) {
                    this.counter = res.data;
                }
                return this.counter;
            }).catch(e => {
                this.counter = {
                    count_exploit: 0,
                    count_threat: 0,
                };
                this.loading = false;
                swal.fire({
                    title: 'Error',
                    text: 'Unable to get counter',
                    showConfirmButton: false,
                    showCloseButton: false,
                    timer: 3000
                });
            });
            this.loading = false;
        }
    }
    
}
</script>

<style>

</style>