import { useState } from 'react';
import { useEmailTemplates, useCreateEmailTemplate, useUpdateEmailTemplate, useDeleteEmailTemplate } from '../hooks/useEmailTemplates';
import { Plus, Edit, Trash2, X, Save, Copy } from 'lucide-react';
import type { EmailTemplate } from '../types';

interface EmailTemplateManagerProps {
  onClose: () => void;
  onSelectTemplate?: (template: EmailTemplate) => void;
  selectMode?: boolean;
}

const defaultVariables = `Available variables:
{{studio_name}} - Studio name
{{contact_name}} - Full contact name
{{first_name}} - Contact first name
{{my_name}} - Your name (Lucas Fulks)`;

export function EmailTemplateManager({ onClose, onSelectTemplate, selectMode = false }: EmailTemplateManagerProps) {
  const { data: templatesData, isLoading } = useEmailTemplates();
  const createMutation = useCreateEmailTemplate();
  const updateMutation = useUpdateEmailTemplate();
  const deleteMutation = useDeleteEmailTemplate();
  
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'introduction',
    subject: '',
    body: '',
  });

  const templates = templatesData?.items || [];

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({
        ...formData,
        variables: defaultVariables,
        is_active: true,
      });
      setIsCreating(false);
      setFormData({ name: '', description: '', category: 'introduction', subject: '', body: '' });
    } catch (error) {
      console.error('Failed to create template:', error);
    }
  };

  const handleUpdate = async () => {
    if (!editingTemplate) return;
    try {
      await updateMutation.mutateAsync({
        id: editingTemplate.id,
        data: formData,
      });
      setEditingTemplate(null);
    } catch (error) {
      console.error('Failed to update template:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch (error) {
      console.error('Failed to delete template:', error);
    }
  };

  const startEdit = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      category: template.category || 'introduction',
      subject: template.subject,
      body: template.body,
    });
  };

  const startCreate = () => {
    setIsCreating(true);
    setFormData({ name: '', description: '', category: 'introduction', subject: '', body: '' });
  };

  const cancelEdit = () => {
    setEditingTemplate(null);
    setIsCreating(false);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold">
            {selectMode ? 'Select Email Template' : 'Email Templates'}
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {isLoading ? (
            <div className="text-center py-8">Loading templates...</div>
          ) : (
            <>
              {/* Create/Edit Form */}
              {(isCreating || editingTemplate) && (
                <div className="bg-gray-50 p-4 rounded-lg mb-4">
                  <h3 className="font-medium mb-3">
                    {isCreating ? 'Create New Template' : 'Edit Template'}
                  </h3>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="e.g., Partnership Introduction"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                      <select
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                      >
                        <option value="introduction">Introduction</option>
                        <option value="follow_up">Follow Up</option>
                        <option value="art_product">Art Product</option>
                        <option value="liveops">LiveOps</option>
                        <option value="general">General</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <input
                        type="text"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="Brief description of when to use this template"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Subject *</label>
                      <input
                        type="text"
                        value={formData.subject}
                        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        placeholder="e.g., Partnership opportunity - {{studio_name}}"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Body *</label>
                      <textarea
                        value={formData.body}
                        onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg h-40 font-mono text-sm"
                        placeholder={`Hi {{first_name}},\n\nI'm reaching out about...`}
                      />
                    </div>

                    <div className="bg-blue-50 p-3 rounded text-sm text-blue-800">
                      <p className="font-medium mb-1">Available variables:</p>
                      <code className="text-xs">{'{{studio_name}} {{contact_name}} {{first_name}} {{my_name}}'}</code>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={isCreating ? handleCreate : handleUpdate}
                        className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        {isCreating ? 'Create' : 'Save'}
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Template List */}
              {!isCreating && !editingTemplate && (
                <>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-medium">Your Templates ({templates.length})</h3>
                    {!selectMode && (
                      <button
                        onClick={startCreate}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        New Template
                      </button>
                    )}
                  </div>

                  <div className="space-y-2">
                    {templates.map((template) => (
                      <div
                        key={template.id}
                        className={`border rounded-lg p-4 hover:border-blue-300 transition-colors ${
                          selectMode ? 'cursor-pointer hover:bg-blue-50' : ''
                        }`}
                        onClick={() => selectMode && onSelectTemplate?.(template)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{template.name}</h4>
                              {template.is_default && (
                                <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded">
                                  Default
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                              <span className="bg-gray-100 px-2 py-1 rounded">{template.category}</span>
                              <span>Used {template.usage_count} times</span>
                            </div>
                            <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                              <p className="font-medium text-gray-700">{template.subject}</p>
                            </div>
                          </div>

                          {!selectMode && (
                            <div className="flex gap-1 ml-4">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  startEdit(template);
                                }}
                                className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDelete(template.id);
                                }}
                                className="p-2 text-red-600 hover:bg-red-50 rounded"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          )}

                          {selectMode && (
                            <button
                              onClick={() => onSelectTemplate?.(template)}
                              className="ml-4 bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700"
                            >
                              Use
                            </button>
                          )}
                        </div>
                      </div>
                    ))}

                    {templates.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        No templates yet. Create your first one!
                      </div>
                    )}
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
