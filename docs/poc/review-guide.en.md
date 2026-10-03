# Support-team PoC review guide — local review preparation

[한국어 안내](review-guide.md)

This is a working internal PoC, not the final product or evidence of clinical effectiveness. It uses independent synthetic data. Actual support-team feedback is still pending; automated checks do not count as human review.

## Start and select English

Follow the Python and Node setup in the [runbook](../development/runbook.md), then run from the repository root:

```bash
npm --prefix apps/web run build
.venv/bin/python tools/dev/run_demo.py --poc --port 8767
```

Open `http://127.0.0.1:8767` and select **English** under **Interface / 화면 언어**. The interface initially uses Finnish with a Korean guide; select English again after reloading. Expand **English walkthrough and review notes** for instructions.

Interface language and publication language are separate. Changing either does not change the selected user or permissions. Questions, records and source excerpts are preserved exactly; they are not translated. The current publication content channel is Finnish. English publication translation is not implemented. Specialist wording review remains pending.

`--poc` disables both STT and LLM and ignores the local Whisper/Ollama configuration. Direct input performs no AI inference. Each fresh launch creates a separate synthetic database outside the repository and prints its run ID and directory. Existing databases are not automatically reset or deleted. To resume a round, pass `--data-root /absolute/run-directory`. Stop the server with Ctrl+C.

## Prepare independent sessions

Use at least two separate browsers or browser profiles that do not share cookies. Two tabs in the same profile are not independent sessions.

- Family A: **Liisa**.
- Staff: **Koskinen**.
- Family B, with different sharing permissions: **Mikko**.

Keep each role in its own browser. After a reload, select the same role to retrieve saved data. Use independent synthetic examples only. Do not enter real patient, resident, facility or contact information, real care audio, or Veil-derived material.

## Review the care loop

1. As Liisa, enter a Question and Send question. Example: “Was a walk completed today?” Confirm it remains after reloading and selecting Liisa again.
2. As staff, find the same question in the queue. Schedule review or Keep unanswered. Scheduling a review does not answer the question.
3. Open Record and publish. Link the question, choose Direct processing — no LLM and enter Original text. Use a synthetic plan such as “A walk with staff is planned after lunch.” Select Plan — not completed and Outdoor activity and health information.
4. Create draft for review. Confirm the family cannot see the draft. Edit the text if needed, check the new-source acknowledgement and Save change. Review the source, speaker, tense, numbers, scope and answer sufficiency; then Approve record. Approval alone must not publish or mark the question answered.
5. Select Liisa as Recipient and Prepare publication. Review each sentence and its source before Publish approved answer. Publication requires a separate review acknowledgement, including the Finnish-wording check. Do not treat English interface text as proof of Finnish content quality.
6. As Liisa, inspect the published answer and Show source. Confirm a plan is still a plan, not confirmed completion. Verify persistence after reloading.
7. As Mikko, verify the health-related statement and its hidden source are not accessible.
8. In Consent, distinguish a proposed candidate from confirmed sharing. Check that revocation prevents subsequent access. This demo does not establish legal consent validity.

Observe where reviewers get stuck before helping. Record whether they understand approval versus publication, plans versus completed activities, and why recipients see different information. Use the same build, round and scenario when comparing a fix with its retest.

## Record actual feedback

Use the team’s existing approved collaboration or meeting channel. The app does not submit feedback externally. Assign an FB-ID only after receiving real feedback. Do not commit reviewer identities or private raw feedback to the public repository.

```text
FB-ID (assigned after actual feedback):
Round / build commit / anonymous role ID:
Participation: screen-share observer / independent-session user
Screen and action / reproduction steps:
Expected result / actual result:
Impact / suggested improvement:
Question-to-publication, generation, human review and correction times: measured or not measured
Shareable summary / internal reference to private evidence:
Action: required fix / improvement / needs clarification
Fix commit / same-scenario retest result:
```

## Shared review remains pending

The loopback URL works only on the machine running the server. Screen sharing is a demonstration, not independent remote use. Shared deployment requires an approved test server and deployment authority, restricted reviewer access, HTTPS or an approved VPN, server-side role separation, per-round data isolation and controlled reset permissions. The unauthenticated demo role selector must not be exposed directly to the public internet.

The shared environment, review schedule and feedback channel are not yet confirmed. Actual support-team feedback and subsequent fixes/retests are still pending. The next detailed specification will be proposed after that feedback; it is not finalized now. Competition reuse/entry permission remains separately UNCONFIRMED.
