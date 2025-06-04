export async function fetchInitialNarrative() {
  return {
    text: 'Welcome, detective. What would you like to do?',
    character: { name: 'Narrator' },
    choices: [
      { id: 1, text: 'Inspect the crime scene' },
      { id: 2, text: 'Talk to the witness' }
    ],
    allowInput: true
  }
}

export async function submitNarrativeChoice(choiceId) {
  if (choiceId === 1) {
    return {
      text: 'You arrive at the dimly lit crime scene. A sense of dread fills the air.',
      character: { name: 'Narrator' },
      choices: [],
      allowInput: true
    }
  } else if (choiceId === 2) {
    return {
      text: 'The witness seems shaken but agrees to talk. What do you ask first?',
      character: { name: 'Narrator' },
      choices: [
        { id: 3, text: 'What did you see?' },
        { id: 4, text: 'Do you know the victim?' }
      ],
      allowInput: false
    }
  } else {
    return {
      text: `You selected an unknown choice (${choiceId}).`,
      character: { name: 'Narrator' },
      choices: [],
      allowInput: true
    }
  }
}

export async function submitUserInput(inputText) {
  return {
    text: `You said: "${inputText}". Let's continue...`,
    character: { name: 'Narrator' },
    choices: [],
    allowInput: true
  }
}
