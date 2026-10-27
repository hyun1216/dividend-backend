// src/components/common/Modal.tsx
'use client';

import React, { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'max-w-md',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-stone-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 transition-all">
      <div className={`bg-white border border-stone-300 ${maxWidth} w-full shadow-xl overflow-hidden flex flex-col max-h-[85vh]`}>
        <div className="p-4 border-b border-stone-200 flex justify-between items-center bg-stone-50">
          <h2 className="text-xs font-bold text-stone-800 uppercase tracking-wider flex items-center gap-1.5">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-stone-400 hover:text-stone-800 font-bold text-xl px-2 py-0.5"
            aria-label="닫기"
          >
            &times;
          </button>
        </div>
        <div className="p-5 flex flex-col gap-4 overflow-y-auto text-xs text-stone-600 leading-relaxed">
          {children}
        </div>
      </div>
    </div>
  );
};
