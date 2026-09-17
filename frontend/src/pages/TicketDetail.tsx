import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Send } from 'lucide-react';
import api from '../api/client';
import SlaBadge from '../components/SlaBadge';

export default function TicketDetail() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [commentBody, setCommentBody] = useState('');
  const [isInternal, setIsInternal] = useState(false);

  const { data: ticket, isLoading } = useQuery({
    queryKey: ['ticket', id],
    queryFn: async () => {
      const res = await api.get(`/tickets/${id}`);
      return res.data;
    }
  });

  const addComment = useMutation({
    mutationFn: async () => {
      await api.post(`/tickets/${id}/comments`, {
        body: commentBody,
        is_internal_note: isInternal
      });
    },
    onSuccess: () => {
      setCommentBody('');
      setIsInternal(false);
      queryClient.invalidateQueries({ queryKey: ['ticket', id] });
    }
  });

  if (isLoading) return <div className="p-8 text-slate-400">Loading details...</div>;
  if (!ticket) return <div className="p-8 text-slate-400">Ticket not found</div>;

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/tickets" className="text-slate-400 hover:text-white transition-colors">
              <ArrowLeft size={20} />
            </Link>
            <div>
              <h1 className="text-xl font-semibold text-white">{ticket.subject}</h1>
              <div className="text-sm text-slate-500 font-mono mt-0.5">#{ticket.id}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
             <SlaBadge 
                dueAt={ticket.sla_resolution_due_at} 
                isBreached={ticket.resolution_breached}
                isResolved={!!ticket.resolved_at}
                label="Resolution SLA" 
              />
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-3 gap-8">
        {/* Main Content: Conversation */}
        <div className="col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="font-medium text-slate-200">Description</span>
              <span className="text-xs text-slate-500">{new Date(ticket.created_at).toLocaleString()}</span>
            </div>
            <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{ticket.description}</p>
          </div>

          {/* Placeholder for actual comments list */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Activity</h3>
            <div className="text-slate-500 italic text-sm">No comments yet.</div>
          </div>

          {/* Reply Box */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all">
            <textarea
              value={commentBody}
              onChange={e => setCommentBody(e.target.value)}
              placeholder="Type your reply here..."
              className="w-full bg-transparent border-none text-slate-200 placeholder-slate-600 p-4 min-h-[120px] resize-y focus:ring-0 sm:text-sm"
            />
            <div className="bg-slate-800/50 px-4 py-3 border-t border-slate-800 flex justify-between items-center">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isInternal}
                  onChange={e => setIsInternal(e.target.checked)}
                  className="rounded border-slate-600 bg-slate-900 text-amber-500 focus:ring-amber-500/20"
                />
                <span className="text-sm text-slate-400 font-medium select-none">Internal Note</span>
              </label>
              <button
                onClick={() => addComment.mutate()}
                disabled={!commentBody.trim() || addComment.isPending}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-1.5 rounded-md font-medium transition-colors flex items-center gap-2 text-sm shadow-sm"
              >
                {addComment.isPending ? 'Sending...' : 'Send Reply'}
                <Send size={14} />
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar: Metadata */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-white mb-4">Ticket Details</h3>
            <div className="space-y-4 text-sm">
              <div>
                <div className="text-slate-500 mb-1">Status</div>
                <select 
                  className="w-full bg-slate-800 border border-slate-700 text-slate-200 rounded-md py-1.5 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  defaultValue={ticket.status}
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="waiting_on_customer">Waiting on Customer</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
              <div>
                <div className="text-slate-500 mb-1">Priority</div>
                <div className="text-slate-200 capitalize font-medium">{ticket.priority}</div>
              </div>
              <div>
                <div className="text-slate-500 mb-1">First Response</div>
                 <SlaBadge 
                  dueAt={ticket.sla_first_response_due_at} 
                  isBreached={ticket.first_response_breached}
                  isResolved={ticket.status !== 'open'}
                  label="Due" 
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
