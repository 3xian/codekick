// Controller-only behavioral oracle for the original GitLab migration report.
package migrations

import (
	"net/http"
	"os"
	"testing"

	"code.gitea.io/gitea/modules/json"

	"github.com/stretchr/testify/require"
	gitlab "gitlab.com/gitlab-org/api/client-go"
)

func TestCodeKickGitlabHistoricalReleaseMigration(t *testing.T) {
	payload, err := os.ReadFile("testdata/codekick_gitlab_releases.json")
	require.NoError(t, err)
	var original []*gitlab.Release
	require.NoError(t, json.Unmarshal(payload, &original))
	// The frozen issue-linked release has four source archives and seven links.
	require.Equal(t, 1, len(original))
	require.Equal(t, 4, len(original[0].Assets.Sources))
	require.Equal(t, 7, len(original[0].Assets.Links))

	mux, server, client := gitlabClientMockSetup(t)
	t.Cleanup(server.Close)
	mux.HandleFunc("/api/v4/projects/40064817/releases", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(payload)
	})
	downloader := &GitlabDownloader{
		client:     client,
		repoID:     40064817,
		baseURL:    server.URL,
		maxPerPage: 50,
	}
	migrated, err := downloader.GetReleases(t.Context())
	require.NoError(t, err)
	require.Equal(t, 1, len(migrated))
	require.Equal(t, original[0].TagName, migrated[0].TagName)
	require.Equal(t, original[0].Name, migrated[0].Name)
	require.Equal(t, original[0].Commit.ID, migrated[0].TargetCommitish)
	require.Equal(t, original[0].Description, migrated[0].Body)

	expectedLinks := make(map[int64]string, len(original[0].Assets.Links))
	for _, link := range original[0].Assets.Links {
		expectedLinks[int64(link.ID)] = link.Name
	}
	actualLinks := make(map[int64]string, len(migrated[0].Assets))
	for _, asset := range migrated[0].Assets {
		if _, duplicate := actualLinks[asset.ID]; duplicate {
			t.Fatalf("duplicate migrated release link ID %d", asset.ID)
		}
		actualLinks[asset.ID] = asset.Name
	}
	require.Equal(t, expectedLinks, actualLinks)
}
