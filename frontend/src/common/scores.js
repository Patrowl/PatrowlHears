export default {
  methods: {
    calcVulnScore(subvector, m_values) {
      if (m_values == undefined || Object.keys(m_values).length === 0) return 0;
      let score = 0.0;
      let m = "";
      let metrics = [];
      for(let i = 0; i < subvector.length; i++) {
        m = subvector[i].split(':');
        m[0] === "AV" && !['N', 'A', 'L'].includes(m[1]) ? score += m_values.cvss2.access.vector.default:null;
        m[0] === "AV" && m[1] === 'N' ? score += m_values.cvss2.access.vector.network:null;
        m[0] === "AV" && m[1] === 'A' ? score += m_values.cvss2.access.vector.adjacent:null;
        m[0] === "AV" && m[1] === 'L' ? score += m_values.cvss2.access.vector.local:null;
        m[0] === "AV" ? metrics.push("AV"):null;

        m[0] === "AC" && !['L', 'M', 'H'].includes(m[1]) ? score += m_values.cvss2.access.complexity.default:null;
        m[0] === "AC" && m[1] === 'L' ? score += m_values.cvss2.access.complexity.low:null;
        m[0] === "AC" && m[1] === 'M' ? score += m_values.cvss2.access.complexity.medium:null;
        m[0] === "AC" && m[1] === 'H' ? score += m_values.cvss2.access.complexity.high:null;
        m[0] === "AC" ? metrics.push("AC"):null;

        m[0] === "Au" && !['N', 'S', 'M'].includes(m[1]) ? score += m_values.cvss2.access.authentication.default:null;
        m[0] === "Au" && m[1] === 'N' ? score += m_values.cvss2.access.authentication.none:null;
        m[0] === "Au" && m[1] === 'S' ? score += m_values.cvss2.access.authentication.single:null;
        m[0] === "Au" && m[1] === 'M' ? score += m_values.cvss2.access.authentication.multiple:null;
        m[0] === "Au" ? metrics.push("Au"):null;

        m[0] === "C" && !['N', 'L', 'H'].includes(m[1]) ? score += m_values.cvss2.impact.confidentiality.default:null;
        m[0] === "C" && m[1] === 'N' ? score += m_values.cvss2.impact.confidentiality.none:null;
        m[0] === "C" && m[1] === 'L' ? score += m_values.cvss2.impact.confidentiality.partial:null;
        m[0] === "C" && m[1] === 'H' ? score += m_values.cvss2.impact.confidentiality.complete:null;
        m[0] === "C" ? metrics.push("C"):null;

        m[0] === "I" && !['N', 'L', 'H'].includes(m[1]) ? score += m_values.cvss2.impact.integrity.default:null;
        m[0] === "I" && m[1] === 'N' ? score += m_values.cvss2.impact.integrity.none:null;
        m[0] === "I" && m[1] === 'L' ? score += m_values.cvss2.impact.integrity.partial:null;
        m[0] === "I" && m[1] === 'H' ? score += m_values.cvss2.impact.integrity.complete:null;
        m[0] === "I" ? metrics.push("I"):null;

        m[0] === "A" && !['N', 'L', 'H'].includes(m[1]) ? score += m_values.cvss2.impact.availability.default:null;
        m[0] === "A" && m[1] === 'N' ? score += m_values.cvss2.impact.availability.none:null;
        m[0] === "A" && m[1] === 'L' ? score += m_values.cvss2.impact.availability.partial:null;
        m[0] === "A" && m[1] === 'H' ? score += m_values.cvss2.impact.availability.complete:null;
        m[0] === "A" ? metrics.push("A"):null;

        m[0] === "R" && !['U', 'W', 'T', 'O'].includes(m[1]) ? score += m_values.remediation.default:null;
        m[0] === "R" && m[1] === 'U' ? score += m_values.remediation.unavailable:null;
        m[0] === "R" && m[1] === 'W' ? score += m_values.remediation.workaround:null;
        m[0] === "R" && m[1] === 'T' ? score += m_values.remediation.temporary:null;
        m[0] === "A" && m[1] === 'O' ? score += m_values.remediation.official:null;
        m[0] === "R" ? metrics.push("R"):null;

        m[0] === "VX" && m[1] <= 15 ? score += m_values.age.caps['15']:null;
        m[0] === "VX" && m[1] > 15 && m[1] <= 45 ? score += m_values.age.caps['45']:null;
        m[0] === "VX" && m[1] > 45 ? score += m_values.age.caps['10000000']:null;

        m[0] === "CL" && m[1] === 'Y' ? score += m_values.confirmation.is_confirmed:null;
        // console.log(m + ":" + score)
      }

      // Default values if not set in subvector
      !metrics.includes("AV") ? score += m_values.cvss2.access.vector.default:null;
      !metrics.includes("AC") ? score += m_values.cvss2.access.complexity.default:null;
      !metrics.includes("Au") ? score += m_values.cvss2.access.authentication.default:null;
      !metrics.includes("C") ? score += m_values.cvss2.impact.confidentiality.default:null;
      !metrics.includes("I") ? score += m_values.cvss2.impact.integrity.default:null;
      !metrics.includes("A") ? score += m_values.cvss2.impact.availability.default:null;
      !metrics.includes("VX") ? score += m_values.age.default:null;
      !metrics.includes("R") ? score += m_values.remediation.default:null;

      score > m_values.max_score ? score = m_values.max_score:null;
      return parseFloat(score).toFixed(1);
    },
    calcThreatScore(subvector, m_values) {
      if (m_values == undefined || Object.keys(m_values).length === 0) return 0;
      let score = 0;
      let m = "";
      let metrics = [];
      // console.log(m_values);
      for(let i = 0; i < subvector.length; i++) {
        m = subvector[i].split(':');
        m[0] === "EA" && !['X', 'R', 'U'].includes(m[1]) ? score += m_values.exploit_availability.default:null;
        m[0] === "EA" && m[1] === 'X' ? score += m_values.exploit_availability.unknown:null;
        m[0] === "EA" && m[1] === 'R' ? score += m_values.exploit_availability.private:null;
        m[0] === "EA" && m[1] === 'U' ? score += m_values.exploit_availability.public:null;
        m[0] === "EA" ? metrics.push("EA"):null;

        m[0] === "EM" && !['X', 'U', 'P', 'F'].includes(m[1]) ? score += m_values.exploit_maturity.default:null;
        m[0] === "EM" && m[1] === 'X' ? score += m_values.exploit_maturity.unknown:null;
        m[0] === "EM" && m[1] === 'U' ? score += m_values.exploit_maturity.unproven:null;
        m[0] === "EM" && m[1] === 'P' ? score += m_values.exploit_maturity.poc:null;
        m[0] === "EM" && m[1] === 'F' ? score += m_values.exploit_maturity.functional:null;
        m[0] === "EM" ? metrics.push("EM"):null;

        m[0] === "ET" && !['X', 'L', 'M', 'H'].includes(m[1]) ? score += m_values.exploit_trust.default:null;
        m[0] === "ET" && m[1] === 'X' ? score += m_values.exploit_trust.unknown:null;
        m[0] === "ET" && m[1] === 'L' ? score += m_values.exploit_trust.low:null;
        m[0] === "ET" && m[1] === 'M' ? score += m_values.exploit_trust.medium:null;
        m[0] === "ET" && m[1] === 'H' ? score += m_values.exploit_trust.high:null;
        m[0] === "ET" ? metrics.push("ET"):null;

        m[0] === "EX" && m[1] <= 15 ? score += m_values.exploit_age.caps['15']:null;
        m[0] === "EX" && m[1] > 15 && m[1] <= 45 ? score += m_values.exploit_age.caps['45']:null;
        m[0] === "EX" && m[1] > 45 ? score += m_values.exploit_age.caps['10000000']:null;

        m[0] === "N" && m[1] === 'Y' ? score += m_values.threat_intensity.is_in_the_news:null;
        m[0] === "W" && m[1] === 'Y' ? score += m_values.threat_intensity.is_in_the_wild:null;

      }

      // Default values if not set in subvector
      !metrics.includes("EA") ? score += m_values.exploit_availability.default:null;
      !metrics.includes("EM") ? score += m_values.exploit_maturity.default:null;
      !metrics.includes("ET") ? score += m_values.exploit_trust.default:null;
      !metrics.includes("EX") ? score += m_values.exploit_age.default:null;

      score > m_values.max_score ? score = m_values.max_score:null;
      return parseFloat(score).toFixed(1);
    },
    calcAssetScore(subvector, m_values) {
      if (m_values == undefined || Object.keys(m_values).length === 0) return 0;
      let score = 0;
      let m = "";
      let metrics = [];
      // console.log(m_values);
      for(let i = 0; i < subvector.length; i++) {
        m = subvector[i].split(':');
        m[0] === "Cr" && !['L', 'M', 'H'].includes(m[1]) ? score += m_values.criticality.default:null;
        m[0] === "Cr" && m[1] === 'L' ? score += m_values.criticality.low:null;
        m[0] === "Cr" && m[1] === 'M' ? score += m_values.criticality.medium:null;
        m[0] === "Cr" && m[1] === 'H' ? score += m_values.criticality.high:null;
        m[0] === "Cr" ? metrics.push("Cr"):null;

        m[0] === "E" && !['R', 'I', 'E'].includes(m[1]) ? score += m_values.exposure.default:null;
        m[0] === "E" && m[1] === 'R' ? score += m_values.exposure.restricted:null;
        m[0] === "E" && m[1] === 'I' ? score += m_values.exposure.internal:null;
        m[0] === "E" && m[1] === 'E' ? score += m_values.exposure.external:null;
        m[0] === "E" ? metrics.push("E"):null;

        m[0] === "D" && !['L', 'M', 'H'].includes(m[1]) ? score += m_values.distribution.default:null;
        m[0] === "D" && m[1] === 'L' ? score += m_values.distribution.low:null;
        m[0] === "D" && m[1] === 'M' ? score += m_values.distribution.medium:null;
        m[0] === "D" && m[1] === 'H' ? score += m_values.distribution.high:null;
        m[0] === "D" ? metrics.push("D"):null;
      }

      // Default values if not set in subvector
      !metrics.includes("Cr") ? score += m_values.criticality.default:null;
      !metrics.includes("E") ? score += m_values.exposure.default:null;
      !metrics.includes("D") ? score += m_values.distribution.default:null;

      score > m_values.max_score ? score = m_values.max_score:null;
      return parseFloat(score).toFixed(1);
    },
  },
  mounted() {

  },
  destroyed() {

  }
};
