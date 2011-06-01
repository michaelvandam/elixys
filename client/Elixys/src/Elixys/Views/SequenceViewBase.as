package Elixys.Views
{
	import Elixys.Events.HTTPRequestEvent;
	import Elixys.HTTP.HTTPConnection;
	import Elixys.HTTP.HTTPRequest;
	import Elixys.Objects.*;
	
	import flash.events.EventDispatcher;
	import flash.events.MouseEvent;
	import flash.utils.ByteArray;
	
	import mx.containers.ViewStack;
	import mx.events.FlexEvent;
	
	import spark.components.Button;
	import spark.components.HGroup;
	import spark.components.Label;
	import spark.components.List;

	public class SequenceViewBase extends ViewBase
	{
		/**
		 * Member functions
		 **/

		// Constructor
		public function SequenceViewBase()
		{
			// Call the base constructor
			super();
		}

		// Set the subview parents
		public function SetSubviewParents():void
		{
			// Inform the child views of the parent
			m_pCassetteSubview.SetParent(this);
			m_pAddSubview.SetParent(this);
			m_pEvaporateSubview.SetParent(this);
			m_pTransferSubview.SetParent(this);
			m_pEluteSubview.SetParent(this);
			m_pReactSubview.SetParent(this);
			m_pPromptSubview.SetParent(this);
			m_pInstallSubview.SetParent(this);
			m_pCommentSubview.SetParent(this);
			m_pActivitySubview.SetParent(this);
		}

		// Returns the sequence ID to our child views
		public function GetSequenceID():uint
		{
			return m_nSequenceID;
		}

		// Update server configuration
		public override function UpdateConfiguration(pConfiguration:Configuration):void
		{
			// Remember the server configuration
			m_pServerConfiguration = pConfiguration;

			// Fill the unit operations list if the derived view supports it
			if (m_pUnitOperationsList)
			{
				UpdateUnitOperationsList(m_pUnitOperationsList, pConfiguration.SupportedOperations());
			}
		}
		
		// Update the sequence state
		protected function UpdateSequenceState(pButtons:Array, nSequenceID:uint, nComponentID:uint):void
		{
			// Update our button array with the server data
			if (m_pNavigationButtons != null)
			{
				UpdateButtons(m_pNavigationButtons, pButtons, CreateNewButton);
				function CreateNewButton():spark.components.Button
				{
					// Callback to create our new button
					var pButton:spark.components.Button = new spark.components.Button();
					pButton.width = 150;
					pButton.height = 40;
					pButton.styleName = "button";
					pButton.addEventListener(MouseEvent.CLICK, m_pOnButtonClick);
					return pButton;
				}
			}
			
			// Remember the currently sequence and component
			m_nSequenceID = nSequenceID;
			m_nComponentID = nComponentID;
		}
		
		// Update the sequence sequence
		public function UpdateSequenceSequence(pSequence:Sequence):void
		{
			// Set the sequence name
			m_pSequenceName.text = pSequence.Metadata().Name;
			
			// Fill the operations list
			UpdateSequenceComponentList(m_pSequenceList, pSequence.Components(), m_nComponentID);
		}
		
		// Update the sequence component
		public function UpdateSequenceComponent(pComponent:Component):void
		{
			// Locate the active view
			var pActiveView:ViewBase;
			switch (pComponent.ComponentType)
			{
				case ComponentCassette.TYPE:
					pActiveView = m_pCassetteSubview;
					break;
				
				case ComponentAdd.TYPE:
					pActiveView = m_pAddSubview;
					break;
				
				case ComponentEvaporate.TYPE:
					pActiveView = m_pEvaporateSubview;
					break;
				
				case ComponentTransfer.TYPE:
					pActiveView = m_pTransferSubview;
					break;
				
				case ComponentElute.TYPE:
					pActiveView = m_pEluteSubview;
					break;
				
				case ComponentReact.TYPE:
					pActiveView = m_pReactSubview;
					break;
				
				case ComponentPrompt.TYPE:
					pActiveView = m_pPromptSubview;
					break;
				
				case ComponentInstall.TYPE:
					pActiveView = m_pInstallSubview;
					break;
				
				case ComponentComment.TYPE:
					pActiveView = m_pCommentSubview;
					break;
				
				case ComponentActivity.TYPE:
					pActiveView = m_pActivitySubview;
					break;
				
				default:
					return;
			}
			
			// Show and update the appropriate component
			m_pViewStack.selectedChild = pActiveView;
			pActiveView.UpdateComponent(pComponent);
		}
		
		// Update sequence reagent
		public function UpdateSequenceReagent(pReagent:Reagent):void
		{
			// Update the active view
			var pViewBase:ViewBase = m_pViewStack.selectedChild as ViewBase;
			pViewBase.UpdateReagent(pReagent);
		}
		
		// Post a request to the server
		public function DoPost(pPost:Object, sViewName:String):void
		{
			// Convert the request to a byte array
			var pBody:ByteArray = new ByteArray();
			pBody.writeMultiByte(pPost.toString(), "utf8");
			pBody.position = 0;
			
			// Pass the request up to be sent to the server
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = "POST";
			pHTTPRequest.m_sResource = "/Elixys/" + sViewName;
			pHTTPRequest.m_pBody = pBody;
			dispatchEvent(new HTTPRequestEvent(pHTTPRequest));
		}

		/***
		 * Member variables
		 **/
		
		// Current sequence and component IDs
		protected var m_nSequenceID:uint = 0;
		protected var m_nComponentID:uint = 0;

		// Server configuration
		protected var m_pServerConfiguration:Configuration = null;
		
		// Pointer to the button click handler of the derived class
		protected var m_pOnButtonClick:Function = null;

		// Pointers to the UI component of the derived class
		protected var m_pUnitOperationsList:List = null;
		protected var m_pSequenceName:Label = null;
		protected var m_pSequenceList:List = null;
		protected var m_pNavigationButtons:HGroup = null;
		protected var m_pViewStack:ViewStack = null;
		protected var m_pCassetteSubview:CassetteSubview = null;
		protected var m_pAddSubview:AddSubview = null;
		protected var m_pEvaporateSubview:EvaporateSubview = null;
		protected var m_pTransferSubview:TransferSubview = null;
		protected var m_pEluteSubview:EluteSubview = null;
		protected var m_pReactSubview:ReactSubview = null;
		protected var m_pPromptSubview:PromptSubview = null;
		protected var m_pInstallSubview:InstallSubview = null;
		protected var m_pCommentSubview:CommentSubview = null;
		protected var m_pActivitySubview:ActivitySubview = null;
	}
}