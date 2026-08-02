export type PracticeTechnique =
  | "credential_harvest"
  | "urgency_pii_scam"
  | "social_verify";

export interface PracticeDecoy {
  id: string;
  href: string;
  title: string;
  blurb: string;
  technique: PracticeTechnique;
  techniqueLabel: string;
}

/** Practice traps operators can share with students (authorized training only). */
export const PRACTICE_DECOYS: PracticeDecoy[] = [
  {
    id: "portal",
    href: "/decoy/portal",
    title: "Student Aid Portal",
    blurb: "Fake financial-aid login that harvests school credentials.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "canvas",
    href: "/decoy/canvas",
    title: "Campus Learning (Canvas-style)",
    blurb: "Lookalike LMS login for courses, grades, and assignments.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "wifi",
    href: "/decoy/wifi",
    title: "Campus Wi‑Fi Captive Portal",
    blurb: "Fake “session expired” Wi‑Fi page asking for school login.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "sso",
    href: "/decoy/sso",
    title: "Campus365 SSO",
    blurb: "Microsoft-style school SSO login for email and Office apps.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "bank",
    href: "/decoy/bank",
    title: "Student Bank Alert",
    blurb: "Fake “unusual transfer blocked” banking login.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "zoom",
    href: "/decoy/zoom",
    title: "Class Meeting Login",
    blurb: "Fake Zoom-style join screen that asks for school credentials.",
    technique: "credential_harvest",
    techniqueLabel: "Credential harvest",
  },
  {
    id: "scholarship",
    href: "/decoy/scholarship",
    title: "Merit Award Confirmation",
    blurb: "Urgency + SSN/bank form disguised as scholarship disbursement.",
    technique: "urgency_pii_scam",
    techniqueLabel: "Urgency / PII scam",
  },
  {
    id: "internship",
    href: "/decoy/internship",
    title: "Remote Internship Onboarding",
    blurb: "Fake job offer that demands SSN and bank details for a stipend.",
    technique: "urgency_pii_scam",
    techniqueLabel: "Urgency / PII scam",
  },
  {
    id: "package",
    href: "/decoy/package",
    title: "Parcel Hold Notice",
    blurb: "Delivery-held scam collecting address and a “redelivery fee.”",
    technique: "urgency_pii_scam",
    techniqueLabel: "Urgency / PII scam",
  },
  {
    id: "textbook",
    href: "/decoy/textbook",
    title: "Textbook Buyback Refund",
    blurb: "Fake campus buyback claiming a refund needs bank + SSN.",
    technique: "urgency_pii_scam",
    techniqueLabel: "Urgency / PII scam",
  },
  {
    id: "fafsa",
    href: "/decoy/fafsa",
    title: "FAFSA Correction Hold",
    blurb: "Aid-hold form harvesting SSN, DOB, and direct-deposit info.",
    technique: "urgency_pii_scam",
    techniqueLabel: "Urgency / PII scam",
  },
  {
    id: "discord",
    href: "/decoy/discord",
    title: "Discord Server Verify",
    blurb: "“Keep your access” social verification trap.",
    technique: "social_verify",
    techniqueLabel: "Social verify",
  },
  {
    id: "instagram",
    href: "/decoy/instagram",
    title: "Instagram Account Verify",
    blurb: "“Unusual activity” social verify page targeting account access.",
    technique: "social_verify",
    techniqueLabel: "Social verify",
  },
];
