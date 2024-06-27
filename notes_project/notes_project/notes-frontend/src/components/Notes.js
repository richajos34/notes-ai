// src/components/Notes.js
import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    const { data } = await supabase.from('notes').select('*');
    setNotes(data);
  };

  const addNote = async () => {
    await supabase.from('notes').insert([{ title, content }]);
    fetchNotes();
    setTitle('');
    setContent('');
  };

  return (
    <div>
      <h1>Notes</h1>
      <div>
        <input 
          type="text" 
          placeholder="Title" 
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input 
          type="text" 
          placeholder="Content" 
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button onClick={addNote}>Add Note</button>
      </div>
      {notes.map(note => (
        <div key={note.id}>
          <h2>{note.title}</h2>
          <p>{note.content}</p>
        </div>
      ))}
    </div>
  );
};

export default Notes;
